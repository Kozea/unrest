import logging
from contextlib import contextmanager
from functools import partial

from sqlalchemy import and_, or_
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.strategy_options import Load

from .coercers import Deserialize, Serialize
from .generators.options import Options
from .idiom.unrest import UnRestIdiom

log = logging.getLogger(__name__)


def _call_me_maybe(fun_or_value, *args, **kwargs):
    """Call first argument `fun_or_value` with `*args, **kwargs`
    if it is callable, return it otherwise.
    """
    if callable(fun_or_value):
        return fun_or_value(*args, **kwargs)
    return fun_or_value


def _identity(arg):
    """Identity function, return `arg`"""
    return arg


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
            A validator function takes a #::unrest.rest.Rest#Validatable
            object as parameter and must return the final value for the field
            or raise a `rest.ValidationError(reason)` (where `rest = Unrest()`)
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
        SerializeClass: An alternative #::unrest.coercers#Serialize class.
        DeserializeClass: An alternative #::unrest.coercers#Deserialize class.
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
        idiom=UnRestIdiom,
        SerializeClass=Serialize,
        DeserializeClass=Deserialize,
    ):
        self.unrest = unrest
        self.unrest.rests.append(self)
        self.Model = Model

        self.methods = tuple(methods)
        self.name = name or self.table.name
        self.only = only
        self.exclude = exclude
        self.query_factory = query or (lambda q: q)
        self.properties = [
            self.unrest.Property(property)
            if not isinstance(property, self.unrest.Property)
            else property
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

        self.idiom = idiom(self)

        self.SerializeClass = SerializeClass
        self.DeserializeClass = DeserializeClass

        self._query_alterer = _identity

        self.overrides = {}

        for method in self.methods:
            self.register_method(method)

    def get(self, payload, **pks):
        """
        The GET method

        - With no arguments: Returns all query elements. (/api/model/)
        - With primary keys: Returns the element in query with the primary
            keys. (/api/model/pk)

        # Arguments
            payload: The request content ignored for GET.
            pks: The primary keys in url if any.
        """
        if self.has(pks):
            item = self.get_from_pk(self.query, **pks)
            return self.serialize_all([item] if item else [])

        items = self.query
        return self.serialize_all(items)

    def put(self, payload, **pks):
        """
        The PUT method

        - With no arguments: If allow_batch set to true replace all the
            query elements with the ones in the request payload.
        - With primary keys: Create or replace the element associated
            with the primary keys from the one in the request payload.

        # Arguments
            payload: The request content containing new elements.
            pks: The primary keys in url if any.
        """
        if not payload:
            self.raise_error(400, 'You must provide a payload')

        if self.has(pks):
            for pk, val in pks.items():
                if pk in payload:
                    assert payload[pk] == val, (
                        f'Incoherent primary_key ({pk}) in payload '
                        f'({payload[pk]!r}) and url ({val!r}) for PUT'
                    )
                else:
                    payload[pk] = val
            existingItem = self.get_from_pk(self.query, **pks)
            item = self.deserialize(payload, existingItem or self.Model())
            self.validate(item)
            if existingItem is None:
                self.session.add(item)
            self.session.flush()
            self.session.expire(item)
            return self.serialize_all([item])

        if not self.allow_batch:
            raise self.unrest.RestError(
                406,
                'You must set allow_batch to True '
                'if you want to use batch methods.',
            )

        self.query.delete()
        items = self.deserialize_all(payload)
        self.validate_all(items)
        self.session.add_all(items)
        self.session.flush()
        self.session.expire_all()
        return self.serialize_all(items)

    def post(self, payload, **pks):
        """
        The POST method

        - With no arguments: Add element from request payload.
        - With primary keys: Correspond to new collection creation. Unused.

        # Arguments
            payload: The request content containing the new element.
            pks: The primary keys in url if any.
        """
        if self.has(pks):
            # Create a collection?
            raise self.unrest.RestError(
                501,
                "POST with primary keys corresponds to collection "
                "creation. It's not implemented by default. "
                "If you want to update an item use the PUT method instead",
            )

        if not payload:
            self.raise_error(400, 'You must provide a payload')
        item = self.deserialize(payload, self.Model())
        self.session.add(item)
        self.validate(item)
        self.session.flush()
        self.session.expire(item)
        return self.serialize_all([item])

    def delete(self, payload, **pks):
        """
        The DELETE method

        - With no arguments: If allow_batch set to true delete all query
            elements.
        - With primary keys: Delete the element associated with the primary
            keys.

        # Arguments
            payload: The request content ignored in DELETE.
            pks: The primary keys of the element to delete.
        """
        if self.has(pks):
            item = self.get_from_pk(self.undefered_query, **pks)
            if item is None:
                self.raise_error(404, f'{self.name}({pks!r}) not found')

            self.session.delete(item)
            self.session.flush()
            return self.serialize_all([item])

        if not self.allow_batch:
            raise self.unrest.RestError(
                406,
                'You must set allow_batch to True '
                'if you want to use batch methods.',
            )

        items = self.undefered_query.all()
        self.query.delete()
        self.session.flush()
        return self.serialize_all(items)

    def patch(self, payload, **pks):
        """
        The PATCH method

        - With no arguments: If allow_batch set to true patch existing elements
            with element attributes specified in the request payload.
        - With primary keys: Patch only one

        # Arguments
            payload: The request content containing
                a list of attributes to be patched.
            pks: The primary keys of the element to patch.
        """
        if not payload:
            self.raise_error(400, 'You must provide a payload')

        if self.has(pks):
            for pk, val in pks.items():
                if pk in payload:
                    assert payload[pk] == val, (
                        f'Incoherent primary_key ({pk}) in payload '
                        f'({payload[pk]!r}) and url ({val!r}) for PATCH'
                    )
                else:
                    payload[pk] = val
            item = self.get_from_pk(self.query, **pks)
            if item is None:
                self.raise_error(404, f'{self.name}({pks!r}) not found')
            self.deserialize(payload, item, blank_missing=False)
            self.validate(item)
            self.session.flush()
            self.session.expire(item)
            return self.serialize_all([item])

        if not self.allow_batch:
            raise self.unrest.RestError(
                406,
                'You must set allow_batch to True '
                'if you want to use batch methods.',
            )

        patches = payload['objects']
        # Get all concerned items
        items = self.get_all_from_pks(
            self.query,
            [{pk: patch[pk] for pk in self.primary_keys} for patch in patches],
        )
        if len(items) < len(patches):
            for patch in patches:
                if (
                    len(
                        [
                            it
                            for pk in self.primary_keys
                            for it in items
                            if getattr(it, pk) == patch[pk]
                        ]
                    )
                    == 0
                ):
                    patch = {
                        key: val
                        for key, val in patch.items()
                        if key in self.primary_keys
                    }
                    self.raise_error(404, f'{self.name}({patch}) not found')

        for patch in patches:
            # Get the patch item
            item = [
                it
                for pk in self.primary_keys
                for it in items
                if getattr(it, pk) == patch[pk]
            ][0]
            # Merge only patched colmuns
            self.deserialize(patch, item, blank_missing=False)
        self.validate_all(items)
        self.session.flush()
        self.session.expire_all()
        return self.serialize_all(items)

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
            manual_commit: Set this to True to prevent auto commit after route
                call
        """

        def register_function(function):
            self.overrides[method] = (function, manual_commit)
            if method not in self.methods:
                self.register_method(method)
            return function

        return register_function

    def sub(self, query_factory, **kwargs):
        """
        This methods return a copy of the current rest endpoint and takes a
        `query_factory` argument to alter the current query.

        # Arguments
            query_factory: A function that takes the original query
                in parameter and returns a new query.
            **kwargs: Can be used to override Rest constructor arguments
                (query is not supported)

        # Returns
        A #::unrest.rest#Rest endpoint copied from this one
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
            'fixed': self.fixed,
            'defaults': self.defaults,
        }
        inherited.update(kwargs)
        subrest = self.__class__(self.unrest, self.Model, **inherited)
        subrest.query_factory = lambda q: query_factory(self.query_factory(q))
        return subrest

    def parameters_to_pks(self, parameters):
        """
        Transform query parameters into primary keys mapping with
        deserialized values.
        """
        if not parameters or all(
            value is None for value in parameters.values()
        ):
            return {}

        # In case of column_property or hybrid_property
        prop_by_name = {prop.name: prop for prop in self.properties}
        columns = {
            pk: self.columns.get(pk, prop_by_name.get(pk))
            for pk in self.primary_keys
        }
        deserialize = self.DeserializeClass(parameters, columns)
        return {
            name: deserialize.deserialize(name, column)
            for name, column in columns.items()
        }

    def deserialize(self, payload, item, blank_missing=True):
        """
        Deserialize the payload item in the provided item.

        # Arguments
            payload: The payload containing the item object
            item: An instance of the model to put values in
            blank_missing: Set non-provided by payload item attributes at None
        """

        if blank_missing:
            columns = self.columns
        else:
            # Mind only provided columns
            columns = {
                name: column
                for name, column in self.columns.items()
                if name in payload
            }
        self.set_defaults(payload, columns)
        return self.DeserializeClass(payload, columns).merge(item)

    def deserialize_all(self, payload):
        """
        Deserialize all the payload items.

        # Arguments
            payload: The payload containing the item list
        """
        for item in payload['objects']:
            self.set_defaults(item, self.columns)
        return self.DeserializeClass(payload, self.columns).create(self.Model)

    def serialize(self, item):
        """Serialize an `item` with the given `SerializeClass`"""
        return self.SerializeClass(
            item, self.columns, self.properties, self.relationships
        ).dict()

    def serialize_all(self, items):
        """
        Serialize all items and return a mapping containing:

        # Returns
        A dict containing:

        - objects: The serialized objects
        - primary_keys: The list of primary keys defined for this rest
            endpoint
        - occurences: The number of total occurences (without limit)
        - offset if there's a query offset
        - limit if there's a query limit
        """

        rv = {}
        rv['primary_keys'] = self.primary_keys

        if isinstance(items, Query):
            rv['occurences'] = items.offset(None).limit(None).count()
            if items.selectable._offset is not None:
                rv['offset'] = items.selectable._offset
            if items.selectable._limit is not None:
                rv['limit'] = items.selectable._limit

        rv['objects'] = [self.serialize(item) for item in items]
        if 'occurences' not in rv:
            rv['occurences'] = len(rv['objects'])
        return rv

    def set_defaults(self, payload, columns):
        """Sets in payload item all the fixed and defaults values"""
        for name, column in columns.items():
            if name in self.fixed:
                payload[name] = _call_me_maybe(self.fixed[name], payload)
            elif name not in payload and name in self.defaults:
                payload[name] = _call_me_maybe(self.defaults[name], payload)

    class Validatable(object):
        """
        A validatable class that is used as validators argument.

        # Arguments
            value: The current field value
            name: The current field name
            item: The current item
            ValidationError: The #::unrest.UnRest#ValidationError Exception
                to raise on validation error.
        """

        def __init__(self, value, name, item, ValidationError):
            self.value = value
            self.name = name
            self.item = item
            self.ValidationError = ValidationError

    def validate(self, item, errors=None):
        """
        Validates all validators columns against validators.

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
                    validators = (validators,)
                try:
                    for validator in validators:
                        setattr(
                            item,
                            key,
                            validator(
                                self.Validatable(
                                    getattr(item, key),
                                    key,
                                    item,
                                    self.unrest.ValidationError,
                                )
                            ),
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
                    extra={'errors': [error]},
                )

    def validate_all(self, items):
        """
        Calls validate on all the `items` and raise an error if any does not
        validate.

        # Arguments
            items: A list of item to validate

        # Raises
        A #::unrest.UnRest#RestError on validation error
        """

        errors = []
        for item in items:
            self.validate(item, errors=errors)
        if any(len(error['fields']) for error in errors):
            self.raise_error(500, 'Validation Error', extra={'errors': errors})

    def raise_error(self, status, message, extra=None):
        """Shortcut function to #::unrest.UnRest#raise_error."""
        self.unrest.raise_error(status, message, extra)

    def route(self, method, request):
        """
        This is the entry point for any route method ( #get, #post, #put,
        #delete, #patch, #options ), it takes the #::unrest.util#Request and
        returns the #::unrest.util#Response.

        Exhaustively it
        - converts request parameters into primary keys values
        - calls the current idiom #::unrest.idiom.Idiom#request_to_payload
        - checks auth with `read_auth`, `write_auth` and `auth` if defined
        - calls the route associated with the HTTP `method`, either by default
            or overidden with #declare, with the previously obtained payload
        - commits the session if `manual_commit` is `False` and method is
            amongst modification ones
        - and finally calls #::unrest.idiom.Idiom#data_to_response with the
            return value of the wrapped function to return
            the #::unrest.util#Response

        # Arguments
            method: The HTTP method which is curried in a partial
            request: The current #::unrest.util#Request

        # Returns
        The #::unrest.util#Response of this request
        """
        try:
            pks = self.parameters_to_pks(request.parameters)
            payload = self.idiom.request_to_payload(request)
            return self.wrap_auth_route(method, self.inner_route)(
                request, payload, **pks
            )
        except self.unrest.RestError as e:
            return self.idiom.data_to_response(
                dict(message=e.message, **e.extra), request, e.status
            )

    def wrap_auth_route(self, method, route):
        """This takes a route and apply auth wrappers around it."""
        if method == 'GET' and self.read_auth:
            route = self.read_auth(route)
        if method in ['PUT', 'POST', 'DELETE', 'PATCH'] and self.write_auth:
            route = self.write_auth(route)
        if self.auth:
            route = self.auth(route)
        return route

    def inner_route(self, request, payload, **pks):
        """
        This is the inner route wrapped by the auth wrappers.
        It takes the request and the deserialized payload/primary keys.

        # Arguments
            request: The current #::unrest.util#Request
            payload: The deserialized payload of this request
            **pks: The deserialized primary keys if any

        # Returns
        The #::unrest.util#Response of this request
        """
        method = request.method
        route = getattr(self, method.lower())
        manual_commit = False
        if method in self.overrides:
            route, manual_commit = self.overrides[method]

        with self.query_request(request):
            data = route(payload, **pks)

        if not manual_commit and method in ['PUT', 'POST', 'DELETE', 'PATCH']:
            self.session.commit()

        occurences = (
            f": {data['occurences']} occurences"
            if 'occurences' in data
            else ''
        )
        log.info(f'{method} {self.path}{occurences}')

        return self.idiom.data_to_response(data, request)

    def register_method(self, method):
        """
        Tells the framework to register the #route function or an overidden one
        associated with the http `method`.

        # Arguments
            method: The http method to register the route with
        """
        if method != 'OPTIONS':
            assert method in self.unrest.all, f'Unknown method {method}'

        if method not in self.methods:
            # Add method to the methods array for cohesiveness
            self.methods = (*self.methods, method)

        route = partial(self.route, method)
        route.__name__ = '_'.join((method,) + self.name_parts)
        self.unrest.framework.register_route(
            self.path, method, self.primary_keys, route
        )

        # Register options as soon as a route is registered
        if (
            self.unrest.allow_options
            and method != 'OPTIONS'
            and 'OPTIONS' not in self.methods
        ):
            self.register_method('OPTIONS')

    def has(self, pks):
        """Returns whether the pks dict has values in it."""
        return pks and all(val is not None for val in pks.values())

    def get_from_pk(self, query, **pks):
        """Get the item from `query` that has `**pks` or None if not found."""
        for key, val in pks.items():
            query = query.filter(getattr(self.Model, key) == val)
        return query.first()

    def get_all_from_pks(self, query, items_pks):
        """
        Get all items from `query` correponding to the primary keys `items_pks`
        in one query.
        """
        return query.filter(
            or_(
                *[
                    and_(
                        *[
                            getattr(self.Model, key) == val
                            for key, val in pks.items()
                        ]
                    )
                    for pks in items_pks
                ]
            )
        ).all()

    @contextmanager
    def query_request(self, request):
        """
        Context manager that sets the `_query_alterer` to the idiom alter_query
        and restore it to identity at exit.
        """
        self._query_alterer = partial(self.idiom.alter_query, request)
        yield
        self._query_alterer = _identity

    @property
    def session(self):
        """Shortcut property to the #::unrest#UnRest session."""
        return self.unrest.session

    @property
    def query(self):
        """Gets the current query associated to this Model."""
        query = getattr(self.Model, 'query', None)
        if not query or not isinstance(query, Query):
            query = self.session.query(self.Model)
        return self._query_alterer(self.query_factory(query))

    @property
    def undefered_query(self):
        """Gets the query with all attributes undefered."""
        return self.query.options(Load(self.Model).undefer('*'))

    @property
    def name_parts(self):
        """
        Returns a tuple containing optionally the schema of this table and its
        name.
        """
        if self.table.schema:
            return (self.table.schema, self.name)
        return (self.name,)

    @property
    def path(self):
        """Gets the root path of this endpoint."""
        return '/'.join((self.unrest.root_path,) + self.name_parts)

    @property
    def table(self):
        """This Model table name."""
        return self.Model.__table__

    @property
    def mapper(self):
        """Get the SQLAlchemy mapper of this Model."""
        return inspect(self.Model)

    @property
    def primary_keys(self):
        """This model primary keys names."""
        if self._primary_keys:
            return self._primary_keys

        return [
            self.mapper.get_property_by_column(pk).key
            for pk in self.mapper.primary_key
        ]

    @property
    def columns(self):
        """Gets all columns of this model `column_property` included."""

        def gen():
            for name, column in self.mapper.columns.items():
                if name not in self.primary_keys:
                    if self.only is not None and name not in self.only:
                        continue
                    if self.exclude and name in self.exclude:
                        continue
                yield name, column

        return dict(gen())
