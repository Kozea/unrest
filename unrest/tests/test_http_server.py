from unittest import TestCase

from .crud.delete import DeleteTestCollection
from .crud.delete_pk import DeletePkTestCollection
from .crud.get import GetTestCollection
from .crud.get_pk import GetPkTestCollection
from .crud.patch import PatchTestCollection
from .crud.patch_pk import PatchPkTestCollection
from .crud.post import PostTestCollection
from .crud.post_pk import PostPkTestCollection
from .crud.put import PutTestCollection
from .crud.put_pk import PutPkTestCollection
from .features.auth_decorators import AuthDecoratorsTestCollection
from .features.misc import MiscellaneousTestCollection
from .features.paginated import PaginatedTestCollection
from .features.properties import PropertiesTestCollection
from .features.relationships import RelationshipsTestCollection
from .features.validators import ValidatorsTestCollection
from .helpers.http_server import HTTPServerMixin
from .utils import MiscTests, UnRestTestCase


class HTTPServerTests(MiscTests, UnRestTestCase, HTTPServerMixin, TestCase):
    pass


class HTTPServerGetTests(
    GetTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerGetPkTests(
    GetPkTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerPostTests(
    PostTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerPostPkTests(
    PostPkTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerPutTests(
    PutTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerPutPkTests(
    PutPkTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerPatchTests(
    PatchTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerPatchPkTests(
    PatchPkTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerDeleteTests(
    DeleteTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerDeletePkTests(
    DeletePkTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerAuthDecoratorsTests(
    AuthDecoratorsTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerPaginatedTests(
    PaginatedTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerPropertiesTests(
    PropertiesTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerRelationshipsTests(
    RelationshipsTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerValidatorsTests(
    ValidatorsTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass


class HTTPServerMiscellaneousTests(
    MiscellaneousTestCollection, UnRestTestCase, HTTPServerMixin, TestCase
):
    pass
