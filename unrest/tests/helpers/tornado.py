from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

from ...framework.tornado import TornadoFramework
from .unrest_client import UnRestClient


class SessionRemoverRequestHandler(RequestHandler):
    def on_finish(self):
        super().on_finish()
        self.application.session.remove()


class SessionRemoverTornadoFramework(TornadoFramework):
    __RequestHandlerClass__ = SessionRemoverRequestHandler


class TornadoAsyncClient(AsyncHTTPTestCase):
    def __init__(self, get_app_fun):
        super().__init__()
        self.get_app_fun = get_app_fun

    def get_app(self):
        return self.get_app_fun()

    def runTest(self):
        pass  # pragma: no cover


class TornadoClient(UnRestClient):
    __framework__ = SessionRemoverTornadoFramework

    def setUp(self):
        self.http_client = TornadoAsyncClient(self.get_app)
        self.http_client.setUp()
        super().setUp()

    def get_app(self):
        class MainHandler(SessionRemoverRequestHandler):
            def get(self):
                self.write("A normal route!")

        self.app = Application([(r"/", MainHandler)])
        self.app.session = self.session
        return self.app

    def raw_fetch(self, *args, **kwargs):
        return self.http_client.fetch(*args, **kwargs)

    def tearDown(self):
        self.http_client.tearDown()
