import logging
import re
from types import MethodType
from urllib.parse import parse_qs, urlparse

from ..util import Request

log = logging.getLogger(__name__)


class SimpleUnRest(object):
    """
    Unrest tornado framework implementation.
    This is the framework abstraction you can implement for your own framework

    """

    def __init__(self, app, prefix):
        self.app = app
        self.prefix = prefix
        self.url_map = {}
        parent = self

        class SimpleUnRestHandlerClass(self.app.RequestHandlerClass):
            def __getattribute__(self, name):
                if name.startswith('do_'):
                    method = name.replace('do_', '')

                    def do_METHOD(self):
                        if not self.path.startswith('/' + parent.prefix):
                            return getattr(super(), name)()
                        return self.handle_request(method)

                    return MethodType(do_METHOD, self)
                return super().__getattribute__(name)

            def handle_request(self, method):
                url = urlparse(self.path)
                for path, methods in parent.url_map.items():
                    match = re.fullmatch(path, url.path)
                    if match:
                        if method not in methods:
                            return self.send(405, 'Method Not Allowed')
                        return self.respond(
                            url, method, methods[method], match.groupdict()
                        )
                return self.send(404, 'Not Found')

            def send(self, status, message):
                self.send_response(status)
                self.end_headers()
                self.wfile.write(message.encode('utf-8'))

            def respond(self, url, method, fun, url_parameters):
                length = (
                    int(self.headers['Content-Length'])
                    if 'Content-Length' in self.headers
                    else 0
                )
                body = self.rfile.read(length) if length else ''
                request = Request(
                    url.path,
                    method,
                    url_parameters,
                    parse_qs(url.query),
                    body,
                    self.headers,
                )
                try:
                    response = fun(request)
                except Exception:
                    log.exception('Error on ' + method + ' ' + self.path)
                    return self.send(500, 'Internal Server Error')

                for name, value in response.headers.items():
                    self.headers[name] = value

                self.send(response.status, response.payload)

        self.app.RequestHandlerClass = SimpleUnRestHandlerClass

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

        if path_with_params not in self.url_map:
            self.url_map[path_with_params] = {}

        if method in self.url_map[path_with_params]:
            log.info('Overriding route %s' % name)

        log.info(
            'Registering route %s for %s for %s'
            % (name, path_with_params, method)
        )

        self.url_map[path_with_params][method] = fun

    @property
    def url(self):
        """
        Return the api url root
        """
        # No external in tornado
        return '/' + self.prefix

    def _name(self, name):
        """Generate a unique name for endpoint"""
        return 'unrest__%s__%s' % (self.prefix, name)
