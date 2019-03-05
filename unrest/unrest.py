import json
import logging

from .__about__ import __uri__, __version__
from .coercers import Property
from .generators.openapi import OpenApi
from .generators.options import Options
from .rest import Rest
from .util import Response

log = logging.getLogger(__name__)


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
            can be set afterwards using #init_app.
        session: Your sqlalchemy session,
            can be set afterwards using the #init_session method.
        path: Default '/api', sets the root url path for your endpoints.
        version: Adds a version to the root url path if specified
            (i.e. /api/v2).
        framework: A specific framework class, defaults to auto detect.
        idiom: An idiom class, defaults to #::unrest.idiom.unrest.
        SerializeClass: A global alternative
            for #::unrest.coercers#Serialize class.
        DeserializeClass: A global alternative
            for #::unrest.coercers#Deserialize class.
        RestClass: Replace the default #::unrest.rest#Rest class.
        allow_options: Set it to False to disable OPTIONS requests.
        serve_openapi_file: Set it to False to disable openapi file generation.
        empty_get_as_404: If True return a 404 on get with id not found.
        info: Additional info for the openapi metadata.

    # Frameworks
    Unrest aims to be framework agnostic.
    It currently works with Flask out of the box and provides some other
    frameworks: Tornado and python http.server.
    See #::unrest.framework#Framework.
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
        idiom=None,
        SerializeClass=None,
        DeserializeClass=None,
        RestClass=Rest,
        allow_options=True,
        serve_openapi_file=True,
        OpenApiClass=OpenApi,
        OptionsClass=Options,
        empty_get_as_404=False,
        info={},
    ):
        self.rests = []
        self.path = path
        self.info = info
        self.version = version
        self._framework = framework
        self.framework = None
        self.idiom = idiom
        self.SerializeClass = SerializeClass
        self.DeserializeClass = DeserializeClass
        self.RestClass = RestClass
        self.allow_options = allow_options
        self.serve_openapi_file = serve_openapi_file
        self.OpenApi = OpenApiClass
        self.Options = OptionsClass
        self.empty_get_as_404 = empty_get_as_404
        if app is not None:
            self.init_app(app)
        if session is not None:
            self.init_session(session)

    def init_app(self, app):
        """Sets the app on UnRest if it was missing during instantiation."""
        self.app = app
        if self._framework:
            self.framework = self._framework(app, url=self.root_path)
        else:
            try:
                from flask import Flask
            except ImportError:
                pass
            else:
                if isinstance(app, Flask):
                    from .framework.flask import FlaskFramework

                    self.framework = FlaskFramework(app, url=self.root_path)
        if not self.framework:
            raise NotImplementedError(
                f'Your framework {type(app)} is not recognized. '
                'Please provide a framework argument to UnRest'
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
        """Return this API root path."""
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
            status: The HTTP status code corresponding to the error
                (404 for instance).
            message: The message that will be returned in the json response.
            extra: Mapping of extra fields to return in json response.
        """
        raise self.RestError(status, message, extra)

    def __call__(self, *args, **kwargs):
        """Return a #::unrest.rest#Rest instance. See rest entry points."""

        if self.idiom is not None:
            kwargs.setdefault('idiom', self.idiom)
        if self.SerializeClass is not None:
            kwargs.setdefault('SerializeClass', self.SerializeClass)
        if self.DeserializeClass is not None:
            kwargs.setdefault('DeserializeClass', self.DeserializeClass)

        rest = self.RestClass(self, *args, **kwargs)
        return rest

    def register_index(self):
        """Register the API index GET route."""
        self.framework.register_route(
            self.root_path + '/', 'GET', None, self.index
        )

    def index(self, request):
        """The API index GET route."""
        return Response(
            (
                '<h1>unrest <small>api server</small></h1> version '
                f'{__version__} <a href="{__uri__}">unrest</a>'
            )
            + (f' <a href="{self.root_path}/openapi.json">openapi.json</a>')
            if self.serve_openapi_file
            else '',
            {'Content-Type': 'text/html'},
            200,
        )

    def send_json(self, data):
        """
        Send `data` as json.

        # Arguments
            data: An object to send as json.

        # Returns
        The #::unrest.util#Response containing the json data.
        """
        payload = json.dumps(data)
        headers = {'Content-Type': 'application/json'}
        return Response(payload, headers, 200)

    def register_options(self):
        """Register the API index OPTIONS route."""
        self.framework.register_route(
            self.root_path, 'OPTIONS', None, self.options
        )

    def options(self, request):
        """The API index OPTIONS route."""
        return self.send_json(self.Options(self).all())

    def register_openapi(self):
        """Register the openapi route."""
        self.framework.register_route(
            self.root_path + '/openapi.json', 'GET', None, self.openapi
        )

    def openapi(self, request):
        """The API openapi route."""
        return self.send_json(self.OpenApi(self).all())

    def virtual(self, *args, **kwargs):
        if len(args) > 1:
            args = list(args)
            args[1] = []
        else:
            kwargs['methods'] = []
        return self(*args, **kwargs)

    Property = Property
