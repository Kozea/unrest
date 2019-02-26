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
from .helpers.flask import FlaskMixin
from .utils import MiscTests, UnRestTestCase


class FlaskTests(MiscTests, UnRestTestCase, FlaskMixin, TestCase):
    pass


class FlaskGetTests(GetTestCollection, UnRestTestCase, FlaskMixin, TestCase):
    pass


class FlaskGetPkTests(
    GetPkTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass


class FlaskPostTests(PostTestCollection, UnRestTestCase, FlaskMixin, TestCase):
    pass


class FlaskPostPkTests(
    PostPkTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass


class FlaskPutTests(PutTestCollection, UnRestTestCase, FlaskMixin, TestCase):
    pass


class FlaskPutPkTests(
    PutPkTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass


class FlaskPatchTests(
    PatchTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass


class FlaskPatchPkTests(
    PatchPkTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass


class FlaskDeleteTests(
    DeleteTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass


class FlaskDeletePkTests(
    DeletePkTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass


class FlaskAuthDecoratorsTests(
    AuthDecoratorsTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass


class FlaskPaginatedTests(
    PaginatedTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass


class FlaskPropertiesTests(
    PropertiesTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass


class FlaskRelationshipsTests(
    RelationshipsTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass


class FlaskValidatorsTests(
    ValidatorsTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass


class FlaskMiscellaneousTests(
    MiscellaneousTestCollection, UnRestTestCase, FlaskMixin, TestCase
):
    pass
