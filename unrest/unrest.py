import json
import logging

from .__about__ import __uri__, __version__
from .coercers import Property
from .generators.openapi import OpenApi
from .generators.options import Options
from .rest import Rest

log = logging.getLogger('unrest')


class UnRest(object):
    """
    A troubling rest api library for sqlalchemy models.
    This is the main entry point of unrest.

    Common usage is as following:

    ```python
    rest = UnRest(app, session)  # app is your application
    # When called, it instanciate a `Rest` object that will register the
    # REST endpoints. See the `Rest` class.
    rest(Model1)
    rest(Model2)
    ```

    # Arguments
        app: Your web application,
            can be set afterwards using #UnRest.init_app
        session: Your sqlalchemy session,
            can be set afterwards using #UnRest.init_session
            and `init_session` method.
        path: Default '/api', sets the root url path for your endpoints
        version: Adds a version to the root url path if specified
            (i.e. /api/v2)
        framework: Your specific framework class, defaults to auto detect.
        SerializeClass: A global alternative for #Serialize class.
        DeserializeClass: A global alternative for #Deserialize class.
        allow_options: Set it to False to disable OPTIONS requests.
        serve_openapi_file: Set it to False to disable openapi file generation.
        info: Additional info for the openapi metadata.
    Unrest aims to be framework agnostic.
    It currently works with Flask out of the box, for another web framework
    you will have to implement your own Framework class.
    See `FlaskUnRest` in `flask_framework.py`
    """

    class RestError(Exception):
        """
        Exception raised by rest methods. It's catched by the REST method
        wrapper and will return a `status` http error with the specified
        `message`.
        """

        def __init__(self, status, message, extra=None):
            self.status = status
            self.message = message
            self.extra = extra or {}

    class ValidationError(Exception):
        """
        Exception raised by rest validation methods.
        """

        def __init__(self, message):
            self.message = message

    def __init__(
            self,
            app=None,
            session=None,
            path='/api',
            version='',
            framework=None,
            SerializeClass=None,
            DeserializeClass=None,
            allow_options=True,
            serve_openapi_file=True,
            openapi_class=OpenApi,
            options_class=Options,
            info={},
    ):
        self.rests = []
        self.path = path
        self.info = info
        self.version = version
        self._framework = framework
        self.SerializeClass = SerializeClass
        self.DeserializeClass = DeserializeClass
        self.allow_options = allow_options
        self.serve_openapi_file = serve_openapi_file
        self.OpenApi = openapi_class
        self.Options = options_class

        if app is not None:
            self.init_app(app)
        if session is not None:
            self.init_session(session)

    def init_app(self, app):
        """Sets the app on UnRest if it was missing during instantiation."""
        self.app = app
        prefix = self.root_path.lstrip('/').replace('/', '_')
        if self._framework:
            self.framework = self._framework(app, prefix=prefix)
        else:
            try:
                from flask import Flask
            except ImportError:
                pass
            else:
                if isinstance(app, Flask):
                    from .flask_framework import FlaskUnRest
                    self.framework = FlaskUnRest(app, prefix=prefix)
        if not self.framework:
            raise NotImplementedError(
                'Your framework %s is not recognized. '
                'Please provide a framework argument to UnRest' % type(app)
            )
        self.register_index()
        self.allow_options and self.register_options()
        self.serve_openapi_file and self.register_openapi()

    def init_session(self, session):
        """
        Sets the sqlalchemy session on UnRest
        if it was missing during instantiation.
        """
        self.session = session

    @property
    def root_path(self):
        if self.version:
            return '/'.join((self.path, self.version))
        return self.path

    @property
    def all(self):
        """
        Return all supported methods. Useful for the rest
        `method` keyword argument.
        """
        return ['GET', 'PUT', 'POST', 'DELETE', 'PATCH']

    def raise_error(self, status, message, extra=None):
        """
        Raise an error that will be handled by the rest wrapper, which
        will return a json response with status as HTTP status code
        and message as content.

        # Arguments
            status: The http status code corresponding to the error
                (404 for instance)
            message: The message that will be returned in the json response
            extra: Mapping of extra fields to return in json response
        """
        raise self.RestError(status, message, extra)

    def __call__(self, *args, **kwargs):
        """Returns a #unrest.Rest instance. See rest entry points."""

        if self.SerializeClass is not None:
            kwargs.setdefault('SerializeClass', self.SerializeClass)
        if self.DeserializeClass is not None:
            kwargs.setdefault('DeserializeClass', self.DeserializeClass)

        rest = Rest(self, *args, **kwargs)
        return rest

    def register_index(self):
        self.framework.register_route(
            self.root_path + '/', 'GET', None, self.index
        )

    def index(self):
        return (
            '<h1>unrest <small>api server</small></h1> version %s '
            '<a href="%s">unrest</a>'
        ) % (__version__, __uri__) + (
            ' <a href="%s/openapi.json">openapi.json</a>' % self.root_path
        ) if self.serve_openapi_file else ''

    def register_options(self):
        self.framework.register_route(
            self.root_path, 'OPTIONS', None, self.options
        )

    def options(self):
        return self.framework.send_json(json.dumps(self.Options(self).all()))

    def register_openapi(self):
        self.framework.register_route(
            self.root_path + '/openapi.json', 'GET', None, self.openapi
        )

    def openapi(self):
        return self.framework.send_json(json.dumps(self.OpenApi(self).all()))

    Property = Property

    class Response(object):
        def __init__(self, data, wrapper=lambda x: x, status_code=200):
            if isinstance(data, self.__class__):
                self.data = data.data
                self.wrapper = lambda r: wrapper(data.wrapper(r))
            else:
                self.data = data
                self.wrapper = wrapper
            self.status_code = status_code
