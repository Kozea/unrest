import logging
from functools import wraps

from tornado.web import RequestHandler, _ApplicationRouter

from . import Framework
from ..util import Request

log = logging.getLogger(__name__)


class TornadoFramework(Framework):
    """
    Unrest #::unrest.framework#Framework implementation for Tornado.

    Requires [tornado](https://www.tornadoweb.org/) to be installed.
    """

    def __init__(self, app, prefix):
        super().__init__(app, prefix)
        self.router = _ApplicationRouter(app)
        self.app.default_router.add_rules(
            [(r'/' + prefix + r'/(.*)', self.router)]
        )

    def register_route(self, path, method, parameters, function):
        name = self._name(function.__name__.replace(method + '_', ''))
        path_with_params = (
            path
            + '(?:/'
            + '/'.join('(?P<%s>.+)' % param for param in parameters)
            + ')?'
            if parameters
            else path
        )

        Handler = self.router.named_rules.get(name)
        if not Handler:
            Handler = type(name + 'Handler', (RequestHandler,), {})
            self.router.add_rules([(path_with_params, Handler, {}, name)])

        log.info(
            'Registering route %s for %s for %s'
            % (name, path_with_params, method)
        )

        @wraps(function)
        def tornado_fun(self, **url_parameters):
            request = Request(
                self.request.path,
                self.request.method,
                url_parameters,
                self.request.query_arguments,
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
    def url(self):
        return self.app.reverse_url(self._name('index'))
