from tornado.web import Application, RequestHandler

from ...framework.tornado import TornadoFramework


class SessionRemoverRequestHandler(RequestHandler):
    def on_finish(self):
        super().on_finish()
        self.application.session.remove()


class SessionRemoverTornadoFramework(TornadoFramework):
    __RequestHandlerClass__ = SessionRemoverRequestHandler


class TornadoMixin(object):
    __framework__ = SessionRemoverTornadoFramework

    def get_app(self):
        class MainHandler(SessionRemoverRequestHandler):
            def get(self):
                self.write("A normal route!")

        self.app = Application([(r"/", MainHandler)])
        self.app.session = self.session
        return self.app
