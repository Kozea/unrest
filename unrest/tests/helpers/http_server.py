from http.server import BaseHTTPRequestHandler
from io import BytesIO

from ...framework.http_server import HTTPServerFramework
from .unrest_client import UnRestClient


class FakeApp(object):
    def __init__(self, rhc):
        self.RequestHandlerClass = rhc


class FakeResponse(object):
    def __init__(self, code, headers, body):
        self.code = code
        self.headers = headers
        self.body = body


def patch_app(app):
    class FakeRequest(app.RequestHandlerClass):
        def __init__(self, request):
            self.rfile = BytesIO()
            self.rfile.write(request)
            self.rfile.seek(0)
            self.wfile = BytesIO()
            self.handle_one_request()
            self.finish()

        def log_message(self, *args):
            print(*args)

    app.RequestHandlerClass = FakeRequest


class HTTPServerClient(UnRestClient):
    __framework__ = HTTPServerFramework

    def setUp(self):
        self.get_app()
        super().setUp()

    def get_app(self):
        session = self.session

        class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path != '/':
                    self.send_response(404)
                    self.end_headers()
                    return
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'A normal route!')

            def finish(self):
                session.remove()

        self.app = FakeApp(SimpleHTTPRequestHandler)
        patch_app(self.app)
        return self.app

    def raw_fetch(self, url, method='GET', headers={}, body=None):
        if body:
            headers['Content-Length'] = len(body)

        request = '\r\n'.join(
            [f'{method.upper()} {url} HTTP/1.1']
            + [f'{key}:{value}' for key, value in headers.items()]
        )
        if body:
            request += '\r\n\r\n' + body

        server = self.app.RequestHandlerClass(request.encode('iso-8859-1'))
        server.wfile.seek(0)
        res = server.wfile.read().decode('iso-8859-1')
        [head, body] = res.split('\r\n\r\n')
        res_lines = head.split('\r\n')
        [_, code, message] = res_lines[0].split(' ', 2)
        headers = {
            line.split(':')[0]: line.split(':')[1].strip()
            for line in res_lines[1:]
        }

        return FakeResponse(int(code), headers, body.encode('utf-8'))
