import logging
import re
from types import MethodType
from urllib.parse import parse_qs, urlparse

from ..util import Request
from . import Framework

log = logging.getLogger(__name__)


class HTTPServerFramework(Framework):
    """
    Unrest #::unrest.framework#Framework implementation for
    [http.server.HTTPServer](https://docs.python.org/3/library/http.server.html)
    compatible app.

    This exemple implementation requires no external library.
    """

    def __init__(self, app, url):
        super().__init__(app, url)
        self.url_map = {}
        parent = self

        class HTTPServerFrameworkHandlerClass(self.app.RequestHandlerClass):
            """
            http.server.RequestHandlerClass implementation for UnRest
            #Framework
            """

            def __getattribute__(self, name):
                if name.startswith('do_'):
                    method = name.replace('do_', '')

                    def do_METHOD(self):
                        # Handle only requests starting with url
                        if not self.path.startswith(parent.url):
                            return getattr(super(), name)()
                        return self.handle_request(method)

                    return MethodType(do_METHOD, self)
                return super().__getattribute__(name)

            def handle_request(self, method):
                url = urlparse(self.path)
                # Look up in the url_map if we have matching endpoint
                for path, methods in parent.url_map.items():
                    match = re.fullmatch(path, url.path)
                    if match:
                        # With a corresponding method
                        if method not in methods:
                            return self.send(405, 'Method Not Allowed')
                        return self.respond(
                            url, method, methods[method], match.groupdict()
                        )
                return self.send(404, 'Not Found')

            def send(self, status, message, headers=None):
                headers = headers or {}
                self.send_response(status)

                for name, value in headers.items():
                    self.send_header(name, value)
                self.end_headers()

                self.wfile.write(message.encode('utf-8'))

            def respond(self, url, method, function, url_parameters):
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
                    response = function(request)
                except Exception:
                    log.exception(f'Error on {method} {self.path}')
                    return self.send(500, 'Internal Server Error')

                self.send(response.status, response.payload, response.headers)

        self.app.RequestHandlerClass = HTTPServerFrameworkHandlerClass

    def register_route(self, path, method, parameters, function):
        name = self._name(function.__name__.replace(method + '_', ''))
        # Creating an url regex that accept parameters
        if parameters:
            params = '/'.join(f'(?P<{param}>.+)' for param in parameters)
            path_with_params = f'{path}(?:/{params})?'
        else:
            path_with_params = path

        # If this is the first method for path, initialize method mapping
        if path_with_params not in self.url_map:
            self.url_map[path_with_params] = {}

        if method in self.url_map[path_with_params]:
            raise KeyError(
                f'Method {method} is already registered for path {path}'
            )

        log.info(
            f'Registering route {name} for {path_with_params} for {method}'
        )

        # Associate UnRest function with path and method
        self.url_map[path_with_params][method] = function
