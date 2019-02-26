from unittest import TestCase

from .helpers.http_server import HTTPServerMixin
from .utils import MiscTests, UnRestTestCase


class HTTPServerTests(MiscTests, HTTPServerMixin, UnRestTestCase, TestCase):
    pass
