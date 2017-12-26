from sqlalchemy.types import Float

from unrest import UnRest, __about__
from unrest.flask_framework import FlaskUnRest

from ..model import Fruit, Tree
from .openapi_result import openapi


def test_normal(app, db, http):
    rest = UnRest(app, db.session)
    rest(Tree)
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3


def test_path(app, db, http):
    rest = UnRest(app, db.session, '/forest')
    rest(Tree)
    code, json = http.get('/forest/tree')
    assert code == 200
    assert json['occurences'] == 3


def test_version(app, db, http):
    rest = UnRest(app, db.session, version='v3.14')
    rest(Tree)
    code, json = http.get('/api/v3.14/tree')
    assert code == 200
    assert json['occurences'] == 3


def test_path_and_version(app, db, http):
    rest = UnRest(app, db.session, '/forest', 'v3.14')
    rest(Tree)
    code, json = http.get('/forest/v3.14/tree')
    assert code == 200
    assert json['occurences'] == 3


def test_explicit_framework(app, db, http):
    rest = UnRest(app, db.session, framework=FlaskUnRest)
    rest(Tree)
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3


def test_empty_explicit_framework(app, db, http):
    class FakeUnRest(object):
        def __init__(self, app, prefix):
            pass

        def register_route(self, *args, **kwargs):
            pass

        request_json = register_route
        send_json = register_route
        send_error = register_route

    rest = UnRest(app, db.session, framework=FakeUnRest)
    rest(Tree)
    code, _ = http.get('/api/tree')
    assert code == 404


def test_api_options(app, db, http):
    rest = UnRest(app, db.session)
    fruit = rest(Fruit)
    rest(
        Tree,
        methods=rest.all,
        relationships={'fruits': fruit},
        properties=['fruit_colors'],
        allow_batch=True
    )
    code, json = http.options('/api')
    assert code == 200
    assert json == {
        '/api/fruit': {
            'model': 'Fruit',
            'description': 'A bag of fruit',
            'parameters': ['fruit_id'],
            'columns': {
                'age': 'timedelta',
                'color': 'str',
                'fruit_id': 'int',
                'size': 'Decimal',
                'tree_id': 'int'
            },
            'properties': {},
            'relationships': {},
            'methods': ['GET', 'OPTIONS'],
            'batch': False
        },
        '/api/tree': {
            'model': 'Tree',
            'description': "Where money doesn't grow",
            'parameters': ['id'],
            'columns': {
                'id': 'int',
                'name': 'str'
            },
            'properties': {
                'fruit_colors': 'str'
            },
            'relationships': {
                'fruits': {
                    'model': 'Fruit',
                    'description': 'A bag of fruit',
                    'parameters': ['fruit_id'],
                    'columns': {
                        'age': 'timedelta',
                        'color': 'str',
                        'fruit_id': 'int',
                        'size': 'Decimal',
                        'tree_id': 'int'
                    },
                    'properties': {},
                    'relationships': {},
                    'batch': False
                }
            },
            'methods': ['GET', 'PUT', 'POST', 'DELETE', 'PATCH', 'OPTIONS'],
            'batch': True
        }
    }


def test_endpoint_options(app, db, http):
    rest = UnRest(app, db.session, framework=FlaskUnRest)
    fruit = rest(Fruit)
    rest(
        Tree,
        methods=rest.all,
        relationships={'fruits': fruit},
        properties=['fruit_colors'],
        allow_batch=True
    )
    code, json = http.options('/api/fruit')
    assert code == 200
    assert json == {
        'model': 'Fruit',
        'description': 'A bag of fruit',
        'batch': False,
        'parameters': ['fruit_id'],
        'columns': {
            'age': 'timedelta',
            'color': 'str',
            'fruit_id': 'int',
            'size': 'Decimal',
            'tree_id': 'int'
        },
        'properties': {},
        'relationships': {},
        'methods': ['GET', 'OPTIONS']
    }


def test_openapi(app, db, http):
    rest = UnRest(
        app,
        db.session,
        info={
            'description':
                '''# Unrest demo
This is the demo of unrest api.
This api expose the `Tree` and `Fruit` entity Rest methods.
''',
            'contact': {
                'name': __about__.__author__,
                'url': __about__.__uri__,
                'email': __about__.__email__
            },
            'license': {
                'name': __about__.__license__
            }
        }
    )
    fruit = rest(
        Fruit,
        methods=rest.all,
        properties=[rest.Property('square_size', Float())]
    )
    rest(
        Tree,
        methods=rest.all,
        relationships={'fruits': fruit},
        properties=['fruit_colors'],
        allow_batch=True
    )

    code, json = http.get('/api/openapi.json')
    assert code == 200
    assert json == openapi


def test_sub(app, db, http):
    rest = UnRest(app, db.session)

    fruit = rest(
        Fruit,
        methods=rest.all,
        properties=[rest.Property('square_size', Float())]
    )
    tree = rest(
        Tree,
        methods=rest.all,
        relationships={'fruits': fruit},
        properties=['fruit_colors'],
        query=lambda q: q.filter(Tree.name != 'pine'),
        allow_batch=True
    )
    subtree = tree.sub(lambda q: q.filter(Tree.name != 'oak'))
    for key in ['unrest', 'Model', 'methods', 'only', 'exclude', 'properties',
                'relationships', 'allow_batch', 'auth', 'read_auth',
                'write_auth', 'validators', '_primary_keys', 'SerializeClass',
                'DeserializeClass']:
        assert getattr(subtree, key) == getattr(tree, key)
    assert subtree.name == 'subtree'

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 2

    code, json = http.get('/api/subtree')
    assert code == 200
    assert json['occurences'] == 1

    subtree = tree.sub(
        lambda q: q.filter(Tree.name != 'maple'), name='nomaple'
    )
    code, json = http.get('/api/nomaple')
    assert code == 200
    assert json['occurences'] == 1
