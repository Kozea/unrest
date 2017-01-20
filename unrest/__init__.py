from .flask import FlaskUnRest
from sqlalchemy.inspection import inspect


class Rest(object):
    """Model path on /root_path/schema/model if schema is not public"""
    def __init__(self, unrest, Model, methods=['GET'], only=None, exclude=[]):
        self.unrest = unrest
        self.Model = Model
        self.methods = methods
        self.only = only
        self.exclude = exclude

        for method in methods:
            self.register_method(method)

    def get(self, **kwargs):
        if kwargs:
            pks = self.kwargs_to_pks(kwargs)
            model = self.Model.query.get(pks)
            return str(getattr(model, list(kwargs.keys())[0]))
        models = self.Model.query.all()
        return str([
            getattr(model, self.primary_keys[0].name) for model in models])

    def post(self, **kwargs):
        pks = self.kwargs_to_pks(kwargs)
        return 'POST %s %s' % ('.'.join(self.name_parts), pks)

    def put(self, **kwargs):
        pks = self.kwargs_to_pks(kwargs)
        return 'PUT %s %s' % ('.'.join(self.name_parts), pks)

    def delete(self, **kwargs):
        pks = self.kwargs_to_pks(kwargs)
        return 'DELETE %s %s' % ('.'.join(self.name_parts), pks)

    def kwargs_to_pks(self, kwargs):
        return tuple(kwargs.get(pk.name) for pk in self.primary_keys)

    def register_method(self, method, method_fun=None):
            method_fun = method_fun or getattr(self, method.lower())
            method_fun.__func__.__name__ = '_'.join(
                (method_fun.__func__.__name__,) + self.name_parts)
            self.unrest.framework.register_route(
                self.path, method, self.primary_keys,
                method_fun)

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


class UnRest(object):
    """Root path on /path/version/ if version else /path/ """
    def __init__(self, app=None, path='/api', version='', framework=None):
        self.app = app
        self.path = path
        self.version = version
        self.framework = (framework or FlaskUnRest)(app)

    def init_app(self, app):
        self.app = app

    @property
    def root_path(self):
        return '/'.join((self.path, self.version))

    def __call__(self, *args, **kwargs):
        rest = Rest(self, *args, **kwargs)
        return rest
