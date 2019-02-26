from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

from ...framework.tornado import TornadoFramework
from ..utils import UnRestTestCase


class SessionRemoverRequestHandler(RequestHandler):
    def on_finish(self):
        super().on_finish()
        self.application.session.remove()


class SessionRemoverTornadoFramework(TornadoFramework):
    __RequestHandlerClass__ = SessionRemoverRequestHandler


class TornadoMixin(UnRestTestCase, AsyncHTTPTestCase):
    __framework__ = SessionRemoverTornadoFramework

    def get_app(self):
        class MainHandler(SessionRemoverRequestHandler):
            def get(self):
                self.write("A normal route!")

        self.app = Application([(r"/", MainHandler)])
        self.app.session = self.session
        return self.app

    def raw_fetch(self, *args, **kwargs):
        # This gets the AsyncHTTPTestCase fetch
        # (otherwise we get a stack overflow)
        return super(UnRestTestCase, self).fetch(*args, **kwargs)
