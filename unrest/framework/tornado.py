import logging
from functools import wraps

from tornado.web import RequestHandler, _ApplicationRouter

from ..util import Request

log = logging.getLogger(__name__)


class TornadoUnRest(object):
    """
    Unrest tornado framework implementation.
    This is the framework abstraction you can implement for your own framework

    """

    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix
        self.router = _ApplicationRouter(app)
        self.app.default_router.add_rules(
            [(r'/' + prefix + r'/(.*)', self.router)]
        )

    def register_route(self, path, method, parameters, fun):
        """
        Register the given function for `path` and `method` with and without
        `parameters`.

        # Arguments
            path: The url of the endoint without arguments. ('/api/person')
            method: The HTTP method to register the route on.
            parameters: The primary keys of the model that can be given
                after the path. `PrimaryKey('id'), PrimaryKey('type')) -> \
'/api/person/<id>/<type>'`
            fun: The route function
        """
        name = self._name(fun.__name__.replace(method + '_', ''))
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

        @wraps(fun)
        def tornado_fun(self, **url_parameters):
            request = Request(
                self.request.path,
                self.request.method,
                url_parameters,
                self.request.query_arguments,
                self.request.body,
                self.request.headers,
            )

            response = fun(request)
            for name, value in response.headers.items():
                self.set_header(name, value)
            self.set_status(response.status)
            self.write(response.payload)

        setattr(Handler, method.lower(), tornado_fun)

    @property
    def url(self):
        """
        Return the api url root
        """
        # No external in tornado
        return self.app.reverse_url(self._name('index'))

    def _name(self, name):
        """Generate a unique name for endpoint"""
        return 'unrest__%s__%s' % (self.prefix, name)
