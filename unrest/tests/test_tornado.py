from tornado.testing import AsyncHTTPTestCase

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
from .helpers.tornado import TornadoMixin
from .utils import MiscTests, UnRestTestCase


class TornadoTests(MiscTests, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase):
    pass


class TornadoGetTests(
    GetTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoGetPkTests(
    GetPkTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoPostTests(
    PostTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoPostPkTests(
    PostPkTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoPutTests(
    PutTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoPutPkTests(
    PutPkTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoPatchTests(
    PatchTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoPatchPkTests(
    PatchPkTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoDeleteTests(
    DeleteTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoDeletePkTests(
    DeletePkTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoAuthDecoratorsTests(
    AuthDecoratorsTestCollection,
    UnRestTestCase,
    TornadoMixin,
    AsyncHTTPTestCase,
):
    pass


class TornadoPaginatedTests(
    PaginatedTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoPropertiesTests(
    PropertiesTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoRelationshipsTests(
    RelationshipsTestCollection,
    UnRestTestCase,
    TornadoMixin,
    AsyncHTTPTestCase,
):
    pass


class TornadoValidatorsTests(
    ValidatorsTestCollection, UnRestTestCase, TornadoMixin, AsyncHTTPTestCase
):
    pass


class TornadoMiscellaneousTests(
    MiscellaneousTestCollection,
    UnRestTestCase,
    TornadoMixin,
    AsyncHTTPTestCase,
):
    pass
