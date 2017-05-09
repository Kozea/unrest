from unrest import UnRest
from unrest.flask_framework import FlaskUnRest

from ..model import Fruit, Tree


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
        def __init__(self, app):
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
    rest = UnRest(app, db.session, framework=FlaskUnRest)
    fruit = rest(Fruit)
    rest(Tree, methods=rest.all,
         relationships={'fruits': fruit},
         properties=['fruit_colors'],
         allow_batch=True)
    code, json = http.options('/api')
    assert code == 200
    assert json == {
        '/api/fruit': {
            'model': 'Fruit',
            'description': 'A bag of fruit',
            'columns': {
                'age': 'timedelta',
                'color': 'str',
                'fruit_id': 'int',
                'size': 'Decimal',
                'tree_id': 'int'
            },
            'methods': ['GET', 'OPTIONS']
        },
        '/api/tree': {
            'model': 'Tree',
            'description': "Where money doesn't grow",
            'columns': {
                'id': 'int',
                'name': 'str'
            },
            'properties': {
                'fruit_colors': 'The color of fruits'
            },
            'relationships': {
                'fruits': {
                    'model': 'Fruit',
                    'description': 'A bag of fruit',
                    'columns': {
                        'age': 'timedelta',
                        'color': 'str',
                        'fruit_id': 'int',
                        'size': 'Decimal',
                        'tree_id': 'int'
                    }
                }
            },
            'methods': ['GET', 'PUT', 'POST', 'DELETE', 'PATCH', 'OPTIONS'],
            'batch': True
        }
    }


def test_endpoint_options(app, db, http):
    rest = UnRest(app, db.session, framework=FlaskUnRest)
    fruit = rest(Fruit)
    rest(Tree, methods=rest.all,
         relationships={'fruits': fruit},
         properties=['fruit_colors'],
         allow_batch=True)
    code, json = http.options('/api/fruit')
    assert code == 200
    assert json == {
        'model': 'Fruit',
        'description': 'A bag of fruit',
        'columns': {
            'age': 'timedelta',
            'color': 'str',
            'fruit_id': 'int',
            'size': 'Decimal',
            'tree_id': 'int'
        },
        'methods': ['GET', 'OPTIONS']
    }
