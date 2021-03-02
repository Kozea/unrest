import uuid

from sanic import Sanic, response

from ...framework.sanic import SanicFramework
from .unrest_client import UnRestClient


class SanicClient(UnRestClient):
    __framework__ = SanicFramework

    def setUp(self):
        self.get_app()
        super().setUp()

    def get_app(self):
        self.app = Sanic(str(uuid.uuid4()))

        @self.app.route("/")
        async def home(request):
            return response.text("A normal route!")

        @self.app.middleware('response')
        async def after_request(request, response):
            self.app.session.remove()

        self.app.session = self.session
        return self.app

    def raw_fetch(self, url, method='GET', headers={}, body=None):
        if method in ('GET', 'DELETE', 'OPTIONS'):
            data = {}
        else:
            data = {'data': body}
        req, res = getattr(self.app.test_client, method.lower())(
            url, headers=headers, **data
        )
        res.code = res.status
        return res
