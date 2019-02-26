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


class FlaskGetTests(GetTestCollection, FlaskMixin):
    pass


class FlaskGetPkTests(GetPkTestCollection, FlaskMixin):
    pass


class FlaskPostTests(PostTestCollection, FlaskMixin):
    pass


class FlaskPostPkTests(PostPkTestCollection, FlaskMixin):
    pass


class FlaskPutTests(PutTestCollection, FlaskMixin):
    pass


class FlaskPutPkTests(PutPkTestCollection, FlaskMixin):
    pass


class FlaskPatchTests(PatchTestCollection, FlaskMixin):
    pass


class FlaskPatchPkTests(PatchPkTestCollection, FlaskMixin):
    pass


class FlaskDeleteTests(DeleteTestCollection, FlaskMixin):
    pass


class FlaskDeletePkTests(DeletePkTestCollection, FlaskMixin):
    pass


class FlaskAuthDecoratorsTests(AuthDecoratorsTestCollection, FlaskMixin):
    pass


class FlaskPaginatedTests(PaginatedTestCollection, FlaskMixin):
    pass


class FlaskPropertiesTests(PropertiesTestCollection, FlaskMixin):
    pass


class FlaskRelationshipsTests(RelationshipsTestCollection, FlaskMixin):
    pass


class FlaskValidatorsTests(ValidatorsTestCollection, FlaskMixin):
    pass


class FlaskMiscellaneousTests(MiscellaneousTestCollection, FlaskMixin):
    pass
