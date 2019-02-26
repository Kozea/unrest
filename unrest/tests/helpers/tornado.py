from tornado.web import Application, RequestHandler

from ...framework.tornado import TornadoFramework


class TornadoMixin(object):
    __framework__ = TornadoFramework

    def get_app(self):
        class MainHandler(RequestHandler):
            def get(self):
                self.write("A normal route!")

        self.app = Application([(r"/", MainHandler)])
        return self.app
