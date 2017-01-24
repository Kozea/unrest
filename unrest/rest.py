import json
import logging
from functools import wraps

from sqlalchemy.inspection import inspect
from sqlalchemy.schema import Column

from .coercers import Deserialize, Serialize

log = logging.getLogger('unrest.rest')


class RestError(Exception):
    def __init__(self, message, status):
        self.message = message
        self.status = status


class BatchNotAllowed(Exception):
    pass


class Rest(object):
    """
    This is the entry point for generating a REST endpoint for a specific model
    It takes the Unrest instance given by calling it.
    """
    def __init__(self, unrest, Model,
                 methods=['GET'], name=None, only=None, exclude=None,
                 query=None, query_factory=None, allow_batch=False,
                 SerializeClass=Serialize, DeserializeClass=Deserialize):
        self.SerializeClass = SerializeClass
        self.DeserializeClass = DeserializeClass

        self.unrest = unrest
        self.Model = Model
        self.name = name or self.table.name
        self.methods = methods
        self.only = only
        self.allow_batch = allow_batch
        self.exclude = exclude
        self._query = query or self.session().query(Model)
        self.query_factory = query_factory

        for method in methods:
            self.register_method(method)

    def get(self, payload, **pks):
        if self.has(pks):
            item = self.query.filter_by(**pks).first()
            if item is None:
                raise RestError(
                    '%s(%r) not found' % (self.name, pks), 404)

            return self.serialize([item])

        items = self.query
        return self.serialize(items, self.query.count())

    def put(self, payload, **pks):
        if self.has(pks):
            for pk, val in pks.items():
                if pk in payload:
                    assert payload[pk] == val, (
                        'Incoherent primary_key (%s) in payload (%r) '
                        'and url (%r) for PUT' % (pk, payload[pk], val))
                else:
                    payload[pk] = val
            existingItem = self.query.filter_by(**pks).first()
            item = self.deserialize(payload, existingItem or self.Model())
            if existingItem is None:
                self.session.add(item)
            self.session.commit()
            return self.serialize([item])

        if not self.allow_batch:
            raise BatchNotAllowed(
                'You must set allow_batch to True '
                'if you want to use batch methods.')

        self.query.delete()
        items = self.deserialize_all(payload)
        self.session.add_all(items)
        self.session.commit()
        return self.serialize(items, self.query.count())

    def post(self, payload, **pks):
        if self.has(pks):
            # Create a collection?
            raise NotImplemented(
                "You can't create a new collection here. "
                "If you want to update an item use the PUT method")

        item = self.deserialize(payload, self.Model())
        self.session.add(item)
        self.session.commit()
        return self.serialize([item])

    def delete(self, payload, **pks):
        if self.has(pks):
            item = self.query.filter_by(**pks).first()
            if item is None:
                raise RestError(
                    '%s(%r) not found' % (self.name, pks), 404)
            self.session.delete(item)
            self.session.commit()
            return self.serialize([item])

        if not self.allow_batch:
            raise BatchNotAllowed(
                'You must set allow_batch to True '
                'if you want to use batch methods.')

        items = self.query.all()
        count = self.query.count()
        self.query.delete()
        self.session.commit()
        return self.serialize(items, count)

    def declare(self, method):
        def register_fun(fun):
            self.register_method(method, fun)
        return register_fun

    def kwargs_to_pks(self, kwargs):
        if not kwargs:
            return {}
        item = self.Model()
        self.DeserializeClass(kwargs, self.primary_keys).merge(item)
        return {pk.name: getattr(item, pk.name) for pk in self.primary_keys}

    def deserialize(self, payload, item):
        return self.DeserializeClass(payload, self.columns).merge(item)

    def deserialize_all(self, payload):
        return self.DeserializeClass(payload, self.columns).create(self.Model)

    def serialize_object(self, item):
        return self.SerializeClass(item, self.columns).dict()

    def serialize(self, items, count=None):
        if count is None:
            count = len(items)
        return {
            'occurences': count,
            'objects': [
                self.serialize_object(item) for item in items  # Pagination?
            ]
        }

    def wrap_native(self, method):
        @wraps(method)
        def wrapped(**kwargs):
            pks = self.kwargs_to_pks(kwargs)
            json = self.unrest.framework.request_json()
            payload = self.unjson(json)
            try:
                data = method(payload, **pks)
            except RestError as e:
                json = {'message': e.message}
                return self.unrest.framework.send_error(
                    {'message': e.message}, e.status)
            json = self.json(data)
            return self.unrest.framework.send_json(json)
        return wrapped

    def register_method(self, method, method_fun=None):
            method_fun = method_fun or getattr(self, method.lower())
            method_fun = self.wrap_native(method_fun)
            # str() for python 2 compat
            method_fun.__name__ = str('_'.join(
                ('unrest', method) + self.name_parts))
            self.unrest.framework.register_route(
                self.path, method, self.primary_keys,
                method_fun)

    def json(self, data):
        return json.dumps(data)

    def unjson(self, data):
        if data:
            return json.loads(data)

    def has(self, pks):
        return pks and all(val is not None for val in pks.values())

    @property
    def session(self):
        return self.unrest.session

    @property
    def query(self):
        if self.query_factory:
            return self.query_factory(self._query)
        return self._query

    @property
    def name_parts(self):
        if self.name == self.table.name and self.table.schema:
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
        return inspect(self.Model).primary_key

    @property
    def model_columns(self):
        for column in inspect(self.Model).columns:
            if isinstance(column, Column):
                yield column

    @property
    def columns(self):
        def gen():
            for column in self.model_columns:
                if column.name not in [pk.name for pk in self.primary_keys]:
                    if self.only and column.name not in self.only:
                        continue
                    if self.exclude and column.name in self.exclude:
                        continue
                yield column
        return list(gen())
