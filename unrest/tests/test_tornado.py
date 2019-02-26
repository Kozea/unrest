from tornado.testing import AsyncHTTPTestCase

from .helpers.tornado import TornadoMixin
from .utils import MiscTests, UnRestTestCase


class TornadoTests(MiscTests, TornadoMixin, UnRestTestCase, AsyncHTTPTestCase):
    pass
