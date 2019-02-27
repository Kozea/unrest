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
from .features.idiom import IdiomTestCollection
from .features.misc import MiscellaneousTestCollection
from .features.paginated import PaginatedTestCollection
from .features.properties import PropertiesTestCollection
from .features.relationships import RelationshipsTestCollection
from .features.validators import ValidatorsTestCollection
from .helpers.http_server import HTTPServerMixin


class HTTPServerGetTests(GetTestCollection, HTTPServerMixin):
    pass


class HTTPServerGetPkTests(GetPkTestCollection, HTTPServerMixin):
    pass


class HTTPServerPostTests(PostTestCollection, HTTPServerMixin):
    pass


class HTTPServerPostPkTests(PostPkTestCollection, HTTPServerMixin):
    pass


class HTTPServerPutTests(PutTestCollection, HTTPServerMixin):
    pass


class HTTPServerPutPkTests(PutPkTestCollection, HTTPServerMixin):
    pass


class HTTPServerPatchTests(PatchTestCollection, HTTPServerMixin):
    pass


class HTTPServerPatchPkTests(PatchPkTestCollection, HTTPServerMixin):
    pass


class HTTPServerDeleteTests(DeleteTestCollection, HTTPServerMixin):
    pass


class HTTPServerDeletePkTests(DeletePkTestCollection, HTTPServerMixin):
    pass


class HTTPServerAuthDecoratorsTests(
    AuthDecoratorsTestCollection, HTTPServerMixin
):
    pass


class HTTPServerPaginatedTests(PaginatedTestCollection, HTTPServerMixin):
    pass


class HTTPServerPropertiesTests(PropertiesTestCollection, HTTPServerMixin):
    pass


class HTTPServerRelationshipsTests(
    RelationshipsTestCollection, HTTPServerMixin
):
    pass


class HTTPServerValidatorsTests(ValidatorsTestCollection, HTTPServerMixin):
    pass


class HTTPServerMiscellaneousTests(
    MiscellaneousTestCollection, HTTPServerMixin
):
    pass


class HTTPServerIdiomTests(IdiomTestCollection, HTTPServerMixin):
    pass
