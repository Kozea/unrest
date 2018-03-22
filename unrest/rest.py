import json
import logging
from collections import OrderedDict
from copy import deepcopy
from functools import wraps

from sqlalchemy import and_, or_
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.strategy_options import Load
from sqlalchemy.schema import Column

from .coercers import Deserialize, Serialize
from .generators.options import Options

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = Exception

log = logging.getLogger('unrest.rest')


def call_me_maybe(fun_or_value, *args, **kwargs):
    if callable(fun_or_value):
        return fun_or_value(*args, **kwargs)
    return fun_or_value


class Rest(object):
    """
    This is the entry point for generating a REST endpoint for a specific model
    The final uri if the path is '/api' and version 'v2' would be:
    `/api/v2/model` and `/api/v2/model/pk1/pk2` and if model is not in the
    public schema `/api/v2/schema/model` and `/api/v2/schema/model/pk1/pk2`.

    Usage:
    ```python
        rest = UnRest(app)

        def name_validator(field):
            if len(field.value) > 12:
                raise field.ValidationError(
                    'Name is too long (max 12 characters).')
            return field.value

        rest(Person, only=['name', 'sex', 'age'], methods=rest.all,
             query=lambda q: q.filter(Person.age > 16),
             validators={'name': name_validator})
    ```
    # Arguments
        unrest: The unrest instance given automatically on UnRest call.
        Model: The sqlalchemy orm model class.
        methods: The allowed method list on this endpoint. Possible values are
            GET, PUT, POST, DELETE, PATCH and rest.all
        name: If specified replaces the model name in url.
        only: If specified restricts the json fields to this list.
        exclude: If specified removes the json fields in this list.
        query: A function that takes the Model query and returns your specific
            query. Can be useful to filter data for all the methods.
        properties: A list of additional properties to retrieve on the model.
        relationships: A mapping of relationships and rest endpoints to fetch
            with the model.
        allow_batch: Allow batch operations (PUT, DELETE and PATCH)
            without primary key.
        auth: A decorator that will always be called.
        read_auth: A decorator that will be called on GET.
        write_auth: A decorator that will be called on PUT, POST, DELETE
            and PATCH.
        validators: A mapping of field names and validation functions.
            A validator function takes a `Rest.Validatable` object as parameter
            and must return the final value for the field or raise a
            `rest.ValidationError(reason)` (where `rest = Unrest()`)
        validation_error_code: The http return code when the validation fails.
            Defaults to 500
        primary_keys: A list of column names to use as primary_keys
            (use real db primary keys by default)
        defaults: A mapping of column -> values which sets the default value
            of the columns when the column is not present in the payload.
            Can be a callable, in this case it will be called at runtime with
            the payload as argument.
        fixed: A mapping of column -> values which replaces the values
            present or not in the payload. Can be a callable, in this case it
            will be called at runtime with the payload as argument.
        SerializeClass: An alternative #Serialize class.
        DeserializeClass: An alternative #Deserialize class.
    """

    def __init__(
            self,
            unrest,
            Model,
            methods=['GET'],
            name=None,
            only=None,
            exclude=None,
            query=None,
            properties=None,
            relationships=None,
            allow_batch=False,
            auth=None,
            read_auth=None,
            write_auth=None,
            validators=None,
            validation_error_code=500,
            primary_keys=None,
            defaults=None,
            fixed=None,
            SerializeClass=Serialize,
            DeserializeClass=Deserialize
    ):
        self.unrest = unrest
        self.unrest.rests.append(self)
        self.Model = Model

        self.methods = methods[:]
        self.name = name or self.table.name
        self.only = only
        self.exclude = exclude
        self.query_factory = query or (lambda q: q)
        self.properties = [
            self.unrest.Property(property)
            if not isinstance(property, self.unrest.Property) else property
            for property in (properties or [])
        ]
        self.relationships = relationships or {}

        self.allow_batch = allow_batch

        self.auth = auth
        self.read_auth = read_auth
        self.write_auth = write_auth

        self.validators = validators or {}
        self.validation_error_code = validation_error_code
        self._primary_keys = primary_keys
        self.defaults = defaults or {}
        self.fixed = fixed or {}

        self.SerializeClass = SerializeClass
        self.DeserializeClass = DeserializeClass

        if (self.unrest.allow_options and self.methods
                and 'OPTIONS' not in self.methods):
            self.methods.append('OPTIONS')

        for method in self.methods:
            self.register_method(method)

    def get(self, payload, **pks):
        """
        The GET method

        No arguments: Returns all query elements. (/api/model/)
        Primary keys: Returns the element in query with the primary keys or
            404. (/api/model/pk)

        # Arguments
            payload: The json request content ignored for GET.
            pks: The primary keys in url if any.
        """
        if self.has(pks):
            item = self.get_from_pk(self.query, **pks)
            if item is None:
                return self.unrest.Response(
                    self.serialize([]), status_code=404
                )

            return self.serialize([item])

        items = self.query
        return self.serialize(items)

    def put(self, payload, **pks):
        """
        The PUT method

        No arguments: If allow_batch set to true replace all the query elements
            with the ones in the request payload.
        Primary keys: Create or replace the element associated
            with the primary keys from the one in the request payload.

        # Arguments
            payload: The json request content containing new elements.
            pks: The primary keys in url if any.
        """
        if not payload:
            self.raise_error(400, 'You must provide a payload')

        if self.has(pks):
            for pk, val in pks.items():
                if pk in payload:
                    assert payload[pk] == val, (
                        'Incoherent primary_key (%s) in payload (%r) '
                        'and url (%r) for PUT' % (pk, payload[pk], val)
                    )
                else:
                    payload[pk] = val
            existingItem = self.get_from_pk(self.query, **pks)
            previousItem = deepcopy(existingItem)
            item = self.deserialize(payload, existingItem or self.Model())
            self.validate(item, previousItem)
            if existingItem is None:
                self.session.add(item)
            self.session.flush()
            return self.serialize([item])

        if not self.allow_batch:
            raise self.unrest.RestError(
                406, 'You must set allow_batch to True '
                'if you want to use batch methods.'
            )

        self.query.delete()
        items = self.deserialize_all(payload)
        self.validate_all(items)
        self.session.add_all(items)
        self.session.flush()
        return self.serialize(items)

    def post(self, payload, **pks):
        """
        The POST method

        No arguments: Add element from request payload.
        Primary keys: Correspond to new collection creation. Unused.

        # Arguments
            payload: The json request content containing the new element.
            pks: The primary keys in url if any.
        """
        if self.has(pks):
            # Create a collection?
            raise self.unrest.RestError(
                501, "POST with primary keys corresponds to collection "
                "creation. It's not implemented by default. "
                "If you want to update an item use the PUT method instead"
            )

        if not payload:
            self.raise_error(400, 'You must provide a payload')
        item = self.deserialize(payload, self.Model())
        self.session.add(item)
        self.validate(item)
        self.session.flush()
        return self.serialize([item])

    def delete(self, payload, **pks):
        """
        The DELETE method

        No arguments: If allow_batch set to true delete all query elements.
        Primary keys: Delete the element associated with the primary keys.

        # Arguments
            payload: The json request content ignored in DELETE.
            pks: The primary keys of the element to delete.
        """
        if self.has(pks):
            item = self.get_from_pk(self.undefered_query, **pks)
            if item is None:
                self.raise_error(404, '%s(%r) not found' % (self.name, pks))

            self.session.delete(item)
            self.session.flush()
            return self.serialize([item])

        if not self.allow_batch:
            raise self.unrest.RestError(
                406, 'You must set allow_batch to True '
                'if you want to use batch methods.'
            )

        items = self.undefered_query.all()
        self.query.delete()
        self.session.flush()
        return self.serialize(items)

    def patch(self, payload, **pks):
        """
        The PATCH method

        No arguments: If allow_batch set to true patch existing elements
            with element attributes specified in the request payload.
        Primary keys: Patch only one

        # Arguments
            payload: The json request content containing
                a list of attributes to be patched.
            pks: The primary keys of the element to patch.
        """
        if not payload:
            self.raise_error(400, 'You must provide a payload')

        if self.has(pks):
            for pk, val in pks.items():
                if pk in payload:
                    assert payload[pk] == val, (
                        'Incoherent primary_key (%s) in payload (%r) '
                        'and url (%r) for PATCH' % (pk, payload[pk], val)
                    )
                else:
                    payload[pk] = val
            item = self.get_from_pk(self.query, **pks)
            if item is None:
                self.raise_error(404, '%s(%r) not found' % (self.name, pks))
            self.deserialize(payload, item, blank_missing=False)
            self.validate(item)
            self.session.flush()
            return self.serialize([item])

        if not self.allow_batch:
            raise self.unrest.RestError(
                406, 'You must set allow_batch to True '
                'if you want to use batch methods.'
            )

        patches = payload['objects']
        # Get all concerned items
        items = self.get_all_from_pks(
            self.query, [{pk: patch[pk]
                          for pk in self.primary_keys} for patch in patches]
        )
        if len(items) < len(patches):
            for patch in patches:
                if len([it for pk in self.primary_keys for it in items
                        if getattr(it, pk) == patch[pk]]) == 0:
                    self.raise_error(
                        404, '%s(%r) not found' % (
                            self.name, {
                                key: val
                                for key, val in patch.items()
                                if key in self.primary_keys
                            }
                        )
                    )
        for patch in patches:
            # Get the patch item
            item = [
                it for pk in self.primary_keys for it in items
                if getattr(it, pk) == patch[pk]
            ][0]
            # Merge only patched colmuns
            self.deserialize(patch, item, blank_missing=False)
        self.validate_all(items)
        self.session.flush()
        return self.serialize(items)

    def options(self, payload, **pks):
        """
        The OPTIONS method

        Returns a description of this rest endpoint.
        """
        return Options(self.unrest).get_route(self)

    def declare(self, method, manual_commit=False):
        """
        A decorator to register an alternative method.
        The original is still callable with rest.{method}

        ```python
        fruit = rest(Fruit)

        @fruit.declare('GET')
        def get(payload, fruit_id=None):
            rv = fruit.get(payload, fruit_id=fruit_id)
            return {
                'occurences': rv['occurences'],
                'objects': [
                    {'id': obj['fruit_id']} for obj in rv['objects']
                ]
            }
        ```

        # Arguments
            method: The method to override ('GET' for exemple)
            manual_commit: Don't auto commit after the method.
        """

        def register_fun(fun):
            if self.unrest.allow_options and not self.methods:
                self.register_method('OPTIONS')
            self.register_method(method, fun, manual_commit)
            return fun

        return register_fun

    def sub(self, query_factory, **kwargs):
        """This methods return a copy of the current rest endpoint and takes a
        {query_factory} argument to alter the current query.

        # Arguments
            query_factory: A function that takes the original query
                in parameter and returns a new query.
            **kwargs: Can be used to override Rest constructor arguments
                (query is not supported)
        """

        assert not kwargs.get('query'), 'query is not supported on sub rest'
        inherited = {
            'methods': self.methods,
            'name': 'sub' + self.name,
            'only': self.only,
            'exclude': self.exclude,
            'properties': self.properties,
            'relationships': self.relationships,
            'allow_batch': self.allow_batch,
            'auth': self.auth,
            'read_auth': self.read_auth,
            'write_auth': self.write_auth,
            'validators': self.validators,
            'primary_keys': self._primary_keys,
            'SerializeClass': self.SerializeClass,
            'DeserializeClass': self.DeserializeClass,
        }
        inherited.update(kwargs)
        subrest = self.__class__(self.unrest, self.Model, **inherited)
        subrest.query_factory = lambda q: query_factory(self.query_factory(q))
        return subrest

    def kwargs_to_pks(self, kwargs):
        if not kwargs:
            return {}
        item = self.Model()
        self.DeserializeClass(kwargs, self.primary_keys).merge(item)
        return {name: getattr(item, name) for name in self.primary_keys}

    def deserialize(self, payload, item, blank_missing=True):
        if blank_missing:
            columns = self.columns
        else:
            # Mind only provided columns
            columns = {
                name: column
                for name, column in self.columns.items() if name in payload
            }
        self.set_defaults(payload, columns)
        return self.DeserializeClass(payload, columns).merge(item)

    def deserialize_all(self, payload):
        for item in payload['objects']:
            self.set_defaults(item, self.columns)
        return self.DeserializeClass(payload, self.columns).create(self.Model)

    def serialize_object(self, item):
        return self.SerializeClass(
            item, self.columns, self.properties, self.relationships
        ).dict()

    def serialize(self, items):
        rv = {}
        rv['primary_keys'] = list(self.primary_keys.keys())

        if isinstance(items, Query):
            rv['occurences'] = items.offset(None).limit(None).count()
            if items._offset is not None:
                rv['offset'] = items._offset
            if items._limit is not None:
                rv['limit'] = items._limit

        rv['objects'] = [self.serialize_object(item) for item in items]
        if 'occurences' not in rv:
            rv['occurences'] = len(rv['objects'])
        return rv

    def set_defaults(self, payload, columns):
        for name, column in columns.items():
            if name in self.fixed:
                payload[name] = call_me_maybe(self.fixed[name], payload)
            elif name not in payload and name in self.defaults:
                payload[name] = call_me_maybe(self.defaults[name], payload)

    class Validatable(object):
        def __init__(self, value, name, previous, next, ValidationError):
            self.value = value
            self.name = name
            self.previous = previous
            self.next = next
            self.ValidationError = ValidationError

    def validate(self, item, existing=None, errors=None):
        """
        Validates all validators colums against validators.
        Raise RestError if validation errors.
        """
        with self.session.no_autoflush:
            valid = True
            error = {'fields': {}}
            for pk in self.primary_keys:
                error[pk] = getattr(item, pk)

            for key, validators in self.validators.items():
                field_errors = []
                if callable(validators):
                    validators = (validators, )
                try:
                    for validator in validators:
                        setattr(
                            item, key,
                            validator(
                                self.Validatable(
                                    getattr(item, key), key, existing, item,
                                    self.unrest.ValidationError
                                )
                            )
                        )
                except self.unrest.ValidationError as e:
                    valid = False
                    field_errors.append(e.message)
                if field_errors:
                    error['fields'][key] = '\n'.join(field_errors)
            if errors is not None:
                errors.append(error)
            elif not valid:
                self.raise_error(
                    self.validation_error_code,
                    'Validation Error',
                    extra={
                        'errors': [error]
                    }
                )

    def validate_all(self, items):
        errors = []
        for item in items:
            self.validate(item, errors=errors)
        if any(len(error['fields']) for error in errors):
            self.raise_error(500, 'Validation Error', extra={'errors': errors})

    def raise_error(self, status, message, extra=None):
        self.unrest.raise_error(status, message, extra)

    def wrap_native(self, method, method_fun, manual_commit=False):
        @wraps(method_fun)
        def wrapped(**kwargs):
            pks = self.kwargs_to_pks(kwargs)
            json = self.unrest.framework.request_json()
            try:
                try:
                    payload = self.unjson(json)
                except JSONDecodeError as e:
                    self.raise_error(400, 'JSON Error in payload: %s' % e)
                decorated = method_fun
                if method == 'GET' and self.read_auth:
                    decorated = self.read_auth(decorated)
                if (method in ['PUT', 'POST', 'DELETE', 'PATCH']
                        and self.write_auth):
                    decorated = self.write_auth(decorated)
                if self.auth:
                    decorated = self.auth(decorated)

                response = decorated(payload, **pks)

                if not manual_commit and method in ['PUT', 'POST', 'DELETE',
                                                    'PATCH']:
                    self.session.commit()
            except self.unrest.RestError as e:
                return self.unrest.framework.send_error(
                    dict(message=e.message, **e.extra), e.status
                )
            if not isinstance(response, self.unrest.Response):
                response = self.unrest.Response(response)
            log.info(
                '%s %s%s' % (
                    method, self.path,
                    ': %d occurences' % response.data['occurences']
                    if response.data.get('occurences') is not None else ''
                )
            )

            json = self.json(response.data)
            return response.wrapper(
                self.unrest.framework.send_json(json, response.status_code)
            )

        return wrapped

    def register_method(self, method, method_fun=None, manual_commit=False):
        if method != 'OPTIONS':
            assert method in self.unrest.all, 'Unknown method %s' % method
        method_fun = method_fun or getattr(self, method.lower())
        method_fun = self.wrap_native(method, method_fun, manual_commit)
        # str() for python 2 compat
        method_fun.__name__ = str('_'.join((method, ) + self.name_parts))
        self.unrest.framework.register_route(
            self.path, method, self.primary_keys, method_fun
        )

    def json(self, data):
        return json.dumps(data)

    def unjson(self, data):
        if data:
            return json.loads(data)

    def has(self, pks):
        return pks and all(val is not None for val in pks.values())

    def get_from_pk(self, query, **pks):
        for key, val in pks.items():
            query = query.filter(getattr(self.Model, key) == val)
        return query.first()

    def get_all_from_pks(self, query, items_pks):
        return query.filter(
            or_(
                *[
                    and_(
                        *[
                            getattr(self.Model, key) == val
                            for key, val in pks.items()
                        ]
                    ) for pks in items_pks
                ]
            )
        ).all()

    @property
    def session(self):
        return self.unrest.session

    @property
    def query(self):
        if hasattr(self.Model, 'query') and isinstance(self.Model.query, Query
                                                       ):
            query = self.Model.query
        else:
            query = self.session.query(self.Model)
        return self.query_factory(query)

    @property
    def undefered_query(self):
        return self.query.options(Load(self.Model).undefer('*'))

    @property
    def name_parts(self):
        if self.table.schema:
            return (self.table.schema, self.name)
        return (self.name, )

    @property
    def path(self):
        return '/'.join((self.unrest.root_path, ) + self.name_parts)

    @property
    def table(self):
        return self.Model.__table__

    @property
    def primary_keys(self):
        if self._primary_keys:
            return OrderedDict((name, column)
                               for name, column in self.model_columns
                               if name in self._primary_keys)
        ins = inspect(self.Model)
        return OrderedDict((ins.get_property_by_column(pk).key, pk)
                           for pk in ins.primary_key)

    @property
    def model_columns(self):
        for name, column in inspect(self.Model).columns.items():
            if isinstance(column, Column):
                yield name, column

    @property
    def columns(self):
        def gen():
            for name, column in self.model_columns:
                if name not in self.primary_keys:
                    if self.only is not None and name not in self.only:
                        continue
                    if self.exclude and name in self.exclude:
                        continue
                yield name, column

        return dict(gen())
