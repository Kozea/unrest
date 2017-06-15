import json
import logging
from functools import wraps

from sqlalchemy import and_, or_
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.query import Query
from sqlalchemy.schema import Column

from .coercers import Deserialize, Serialize

try:
    from json import JSONDecodeError
except ImportError:
    JSONDecodeError = Exception


log = logging.getLogger('unrest.rest')


class Rest(object):
    """
    This is the entry point for generating a REST endpoint for a specific model
    The final uri if the path is '/api' and version 'v2' would be:
    `/api/v2/model` and `/api/v2/model/pk1/pk2` and if model is not in the
    public schema `/api/v2/schema/model` and `/api/v2/schema/model/pk1/pk2`.

    Usage:
    ```python
        rest = UnRest(app)
        rest(Person, only=['name', 'sex', 'age'], methods=rest.all,
             query=lambda q: q.filter(Person.age > 16))
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
        SerializeClass: An alternative #Serialize class.
        DeserializeClass: An alternative #Deserialize class.
    """
    def __init__(self, unrest, Model,
                 methods=['GET'], name=None, only=None, exclude=None,
                 query=None, properties=None, relationships=None,
                 allow_batch=False, auth=None, read_auth=None, write_auth=None,
                 SerializeClass=Serialize, DeserializeClass=Deserialize):
        self.unrest = unrest
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

        self.SerializeClass = SerializeClass
        self.DeserializeClass = DeserializeClass

        self.infos = self.unrest.infos[self.path]

        self.set_infos()
        if self.unrest.allow_options and self.methods:
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
                self.raise_error(404, '%s(%r) not found' % (self.name, pks))

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
                        'and url (%r) for PUT' % (pk, payload[pk], val))
                else:
                    payload[pk] = val
            existingItem = self.get_from_pk(self.query, **pks)
            item = self.deserialize(payload, existingItem or self.Model())
            if existingItem is None:
                self.session.add(item)
            self.session.commit()
            return self.serialize([item])

        if not self.allow_batch:
            raise self.unrest.RestError(
                406, 'You must set allow_batch to True '
                'if you want to use batch methods.')

        self.query.delete()
        items = self.deserialize_all(payload)
        self.session.add_all(items)
        self.session.commit()
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
                "If you want to update an item use the PUT method instead")

        if not payload:
            self.raise_error(400, 'You must provide a payload')
        item = self.deserialize(payload, self.Model())
        self.session.add(item)
        self.session.commit()
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
            item = self.get_from_pk(self.query, **pks)
            if item is None:
                self.raise_error(404, '%s(%r) not found' % (self.name, pks))

            self.session.delete(item)
            self.session.commit()
            return self.serialize([item])

        if not self.allow_batch:
            raise self.unrest.RestError(
                406, 'You must set allow_batch to True '
                'if you want to use batch methods.')

        items = self.query.all()
        self.query.delete()
        self.session.commit()
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
                        'and url (%r) for PATCH' % (pk, payload[pk], val))
                else:
                    payload[pk] = val
            item = self.get_from_pk(self.query, **pks)
            if item is None:
                self.raise_error(404, '%s(%r) not found' % (self.name, pks))
            self.deserialize(payload, item, blank_missing=False)
            self.session.commit()
            return self.serialize([item])

        if self.has(pks):
            raise self.unrest.RestError(
                501, "PATCH with primary keys corresponds to nothing. "
                "It's not implemented by default. ")

        if not self.allow_batch:
            raise self.unrest.RestError(
                406, 'You must set allow_batch to True '
                'if you want to use batch methods.')

        patches = payload['objects']
        # Get all concerned items
        items = self.get_all_from_pks(self.query, [{
            pk: patch[pk] for pk in self.primary_keys}
            for patch in patches])
        if len(items) < len(patches):
            for patch in patches:
                if len([it for pk in self.primary_keys for it in items
                        if getattr(it, pk) == patch[pk]]) == 0:
                    self.raise_error(404, '%s(%r) not found' % (
                        self.name, {key: val for key, val in patch.items()
                                    if key in self.primary_keys}))
        for patch in patches:
            # Get the patch item
            item = [it
                    for pk in self.primary_keys
                    for it in items if getattr(it, pk) == patch[pk]][0]
            # Merge only patched colmuns
            self.deserialize(patch, item, blank_missing=False)

        self.session.commit()
        return self.serialize(items)

    def options(self, payload):
        """
        The OPTIONS method

        Returns a description of this rest endpoint.
        """
        return self.infos

    def declare(self, method):
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
        """
        def register_fun(fun):
            if self.unrest.allow_options and not self.methods:
                self.register_method('OPTIONS')
            self.register_method(method, fun)
        return register_fun

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
                name: column for name, column in self.columns.items()
                if name in payload}
        return self.DeserializeClass(payload, columns).merge(item)

    def deserialize_all(self, payload):
        return self.DeserializeClass(payload, self.columns).create(self.Model)

    def serialize_object(self, item):
        return self.SerializeClass(
            item, self.columns, self.properties, self.relationships).dict()

    def serialize(self, items):
        rv = {}
        rv['primary_keys'] = list(self.primary_keys.keys())

        if isinstance(items, Query):
            rv['occurences'] = items.offset(None).limit(None).count()
            if items._offset is not None:
                rv['offset'] = items._offset
            if items._limit is not None:
                rv['limit'] = items._limit

        rv['objects'] = [
            self.serialize_object(item) for item in items
        ]
        if 'occurences' not in rv:
            rv['occurences'] = len(rv['objects'])
        return rv

    def raise_error(self, status, message):
        self.unrest.raise_error(status, message)

    def wrap_native(self, method, method_fun):
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
                if (method in ['PUT', 'POST', 'DELETE', 'PATCH'] and
                        self.write_auth):
                    decorated = self.write_auth(decorated)
                if self.auth:
                    decorated = self.auth(decorated)

                response = decorated(payload, **pks)
            except self.unrest.RestError as e:
                return self.unrest.framework.send_error(
                    dict(message=e.message, **e.extra), e.status)
            if not isinstance(response, self.unrest.Response):
                response = self.unrest.Response(response)

            json = self.json(response.data)
            return response.wrapper(self.unrest.framework.send_json(json))
        return wrapped

    def register_method(self, method, method_fun=None):
        if method != 'OPTIONS':
            assert method in self.unrest.all, 'Unknown method %s' % method
        method_fun = method_fun or getattr(self, method.lower())
        method_fun = self.wrap_native(method, method_fun)
        # str() for python 2 compat
        method_fun.__name__ = str('_'.join(
            ('unrest', method) + self.name_parts))
        self.unrest.framework.register_route(
            self.path, method,
            self.primary_keys if method != 'OPTIONS' else None, method_fun)

        self.infos['methods'].append(method)

    def json(self, data):
        return json.dumps(data)

    def unjson(self, data):
        if data:
            return json.loads(data)

    def has(self, pks):
        return pks and all(val is not None for val in pks.values())

    def set_infos(self):
        self.infos['model'] = self.Model.__name__
        if getattr(self.Model, '__doc__', None):
            self.infos['description'] = self.Model.__doc__

        def sqlatype(type):
            try:
                return type.python_type.__name__
            except NotImplementedError:
                return type.__class__.__name__

        self.infos['columns'] = {
            name: sqlatype(column.type)
            for name, column in self.columns.items()
        }

        if self.properties:
            self.infos['properties'] = {
                prop.name: getattr(
                    getattr(self.Model, prop.name), '__doc__', 'Undocumented')
                for prop in self.properties
            }

        if self.relationships:
            self.infos['relationships'] = {
                rel: {k: v for k, v in rest.infos.items() if k != 'methods'}
                for rel, rest in self.relationships.items()
            }

        if self.allow_batch:
            self.infos['batch'] = self.allow_batch

        self.infos['methods'] = []

    def get_from_pk(self, query, **pks):
        for key, val in pks.items():
            query = query.filter(getattr(self.Model, key) == val)
        return query.first()

    def get_all_from_pks(self, query, items_pks):
        return query.filter(
            or_(*[and_(*[
                getattr(self.Model, key) == val
                for key, val in pks.items()
            ]) for pks in items_pks])).all()

    @property
    def session(self):
        return self.unrest.session

    @property
    def query(self):
        if hasattr(self.Model, 'query') and isinstance(
                self.Model.query, Query):
            query = self.Model.query
        else:
            query = self.session.query(self.Model)
        return self.query_factory(query)

    @property
    def name_parts(self):
        if self.table.schema:
            return (self.table.schema, self.name)
        return (self.name,)

    @property
    def path(self):
        return '/'.join((self.unrest.root_path,) + self.name_parts)

    @property
    def table(self):
        return self.Model.__table__

    @property
    def primary_keys(self):
        ins = inspect(self.Model)
        return {ins.get_property_by_column(pk).key: pk
                for pk in ins.primary_key}

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
