import json
import logging

from sqlalchemy.inspection import inspect
from sqlalchemy.schema import Column
from .coercers import Serialize, Deserialize

log = logging.getLogger('unrest')


class RestError(Exception):
    def __init__(self, message, status):
        self.message = message
        self.status = status


class BatchNotAllowed(Exception):
    pass


class Rest(object):
    """Model path on /root_path/schema/model if schema is not public"""
    def __init__(self, unrest, Model,
                 methods=['GET'], name=None, only=None, exclude=None,
                 query=None, query_factory=None, allow_batch=False,
                 SerializeClass=Serialize, DeserializeClass=Deserialize):
        self.SerializeClass = SerializeClass

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

    def get(self, payload, **kwargs):
        if kwargs:
            pks = self.kwargs_to_pks(kwargs)
            item = self.query.filter_by(**pks).first()
            if item is None:
                raise RestError(
                    '%s(%s) not found' % (self.name, pks), 404)

            return self.serialize(item)

        items = self.query
        return self.serialize_all(items)

    def put(self, payload, **kwargs):
        if kwargs:
            pks = self.kwargs_to_pks(kwargs)
            existingItem = self.query.filter_by(**pks).first()
            item = self.deserialize(payload, existingItem or self.Model())
            if existingItem is None:
                self.session.add(item)
            self.session.commit()
            return self.serialize(item)

        if not self.allow_batch:
            raise BatchNotAllowed(
                'You must set allow_batch to True '
                'if you want to use batch methods.')

        self.query.delete()
        items = self.deserialize_all(payload)
        self.session.add_all(items)
        self.session.commit()
        return self.serialize_all(items)

    def post(self, payload, **kwargs):
        if kwargs:
            # Create a collection?
            raise NotImplemented(
                "You can't create a new collection here. "
                "If you want to update an item use the PUT method")

        item = self.deserialize(payload, self.Model())
        self.session.add(item)
        self.session.commit()
        return self.serialize(item)

    def delete(self, payload, **kwargs):
        if kwargs:
            pks = self.kwargs_to_pks(kwargs)
            item = self.query.filter_by(**pks).first()
            if item:
                self.session.remove(item)
            return self.serialize(item)

        if not self.allow_batch:
            raise BatchNotAllowed(
                'You must set allow_batch to True '
                'if you want to use batch methods.')

        items = self.query.all()
        self.query.delete()
        self.session.commit()
        return self.serialize_all(items)

    def kwargs_to_pks(self, kwargs):
        return {pk.name: kwargs.get(pk.name) for pk in self.primary_keys}

    def deserialize(self, payload, item):
        return self.DeserializeClass(payload, self.columns).merge(item)

    def deserialize_all(self, payload, items):
        return self.DeserializeClass(payload, self.columns).create(self.Model)

    def serialize(self, item):
        return self.SerializeClass(item, self.columns).dict()

    def serialize_all(self, query):
        return {
            'occurences': query.count(),
            'objects': [
                self.serialize(item) for item in query  # Pagination ?
            ]
        }

    def wrap_native(self, method):
        def wrapped(**kwargs):
            json = self.unrest.framework.request_json()
            payload = self.unjson(json)
            try:
                data = method(payload, **kwargs)
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
            method_fun.__name__ = '_'.join(
                (method_fun.__name__,) + self.name_parts)
            self.unrest.framework.register_route(
                self.path, method, self.primary_keys,
                method_fun)

    def json(self, data):
        return json.dumps(data)

    def unjson(self, data):
        if data:
            return json.loads(data)

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
        if self.table.schema:
            return (self.table.schema, self.table.name)
        return (self.table.name,)

    @property
    def path(self):
        return '%s%s' % (
            self.unrest.root_path,
            '/'.join(self.name_parts))

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
        for column in self.model_columns:
            if column.name not in [pk.name for pk in self.primary_keys]:
                if self.only and column.name not in self.only:
                    continue
                if self.exclude and column.name in self.exclude:
                    continue
            yield column


class UnRest(object):
    """Root path on /path/version/ if version else /path/ """
    def __init__(self,
                 app=None, session=None,
                 path='/api', version='', framework=None):
        self.path = path
        self.version = version
        self._framework = framework
        if app is not None:
            self.init_app(app)
        if session is not None:
            self.init_session(session)

    def init_app(self, app):
        self.app = app
        if self._framework:
            self.framework = self._framework(app)
        else:
            try:
                from flask import Flask
            except ImportError:
                pass
            else:
                if isinstance(app, Flask):
                    from .flask import FlaskUnRest
                    self.framework = FlaskUnRest(app)
        if not self.framework:
            raise NotImplemented(
                'Your framework %s is not recognized. '
                'Please provide a framework argument to UnRest' % type(app))

    def init_session(self, session):
        self.session = session

    @property
    def root_path(self):
        return '/'.join((self.path, self.version))

    def __call__(self, *args, **kwargs):
        rest = Rest(self, *args, **kwargs)
        return rest
