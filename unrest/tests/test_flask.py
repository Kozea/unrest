from unittest import TestCase

from .helpers.flask import FlaskMixin
from .utils import MiscTests, UnRestTestCase


class FlaskTests(MiscTests, FlaskMixin, UnRestTestCase, TestCase):
    pass
