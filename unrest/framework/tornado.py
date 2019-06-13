import logging
from functools import wraps

from tornado.web import RequestHandler, _ApplicationRouter

from ..util import Request
from . import Framework

log = logging.getLogger(__name__)


class TornadoFramework(Framework):
    """
    Unrest #::unrest.framework#Framework implementation for Tornado.

    Requires [tornado](https://www.tornadoweb.org/) to be installed.
    """

    __RequestHandlerClass__ = RequestHandler

    def __init__(self, app, url):
        super().__init__(app, url)
        self.router = _ApplicationRouter(app)
        self.app.default_router.add_rules([(url + r'(.*)', self.router)])

    def register_route(self, path, method, parameters, function):
        name = self._name(function.__name__.replace(method + '_', ''))
        # Creating an url regex that accept parameters
        if parameters:
            params = '/'.join(f'(?P<{param}>.+)' for param in parameters)
            path_with_params = f'{path}(?:/{params})?'
        else:
            path_with_params = path

        Handler = self.router.named_rules.get(path_with_params)
        if not Handler:
            Handler = type(
                name + 'Handler', (self.__RequestHandlerClass__,), {}
            )
            self.router.add_rules(
                [(path_with_params, Handler, {}, path_with_params)]
            )
        elif getattr(Handler, 'target', None):
            # If Handler has been wrapper by a Rule
            Handler = Handler.target

        if hasattr(Handler, method.lower()) and hasattr(
            getattr(Handler, method.lower()), '__wrapped__'
        ):
            raise KeyError(
                f'Method {method} is already registered for path {path}'
            )

        log.info(
            f'Registering route {name} for {path_with_params} for {method}'
        )

        @wraps(function)
        def tornado_fun(self, **url_parameters):
            request = Request(
                self.request.path,
                self.request.method,
                url_parameters,
                {
                    key: [val.decode('utf-8') for val in values]
                    for key, values in self.request.query_arguments.items()
                },
                self.request.body,
                self.request.headers,
            )

            response = function(request)
            for name, value in response.headers.items():
                self.set_header(name, value)
            self.set_status(response.status)
            self.write(response.payload)

        setattr(Handler, method.lower(), tornado_fun)

    @property
    def external_url(self):
        return self.app.reverse_url(self.url)
