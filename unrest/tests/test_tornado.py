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


class TornadoGetTests(GetTestCollection, TornadoMixin):
    pass


class TornadoGetPkTests(GetPkTestCollection, TornadoMixin):
    pass


class TornadoPostTests(PostTestCollection, TornadoMixin):
    pass


class TornadoPostPkTests(PostPkTestCollection, TornadoMixin):
    pass


class TornadoPutTests(PutTestCollection, TornadoMixin):
    pass


class TornadoPutPkTests(PutPkTestCollection, TornadoMixin):
    pass


class TornadoPatchTests(PatchTestCollection, TornadoMixin):
    pass


class TornadoPatchPkTests(PatchPkTestCollection, TornadoMixin):
    pass


class TornadoDeleteTests(DeleteTestCollection, TornadoMixin):
    pass


class TornadoDeletePkTests(DeletePkTestCollection, TornadoMixin):
    pass


class TornadoAuthDecoratorsTests(AuthDecoratorsTestCollection, TornadoMixin):
    pass


class TornadoPaginatedTests(PaginatedTestCollection, TornadoMixin):
    pass


class TornadoPropertiesTests(PropertiesTestCollection, TornadoMixin):
    pass


class TornadoRelationshipsTests(RelationshipsTestCollection, TornadoMixin):
    pass


class TornadoValidatorsTests(ValidatorsTestCollection, TornadoMixin):
    pass


class TornadoMiscellaneousTests(MiscellaneousTestCollection, TornadoMixin):
    pass
