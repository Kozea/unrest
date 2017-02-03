from unrest import UnRest
from unrest.flask_framework import FlaskUnRest

from ..model import Tree, Fruit


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


def test_api(app, db, http):
    rest = UnRest(app, db.session, framework=FlaskUnRest)
    rest(Tree, methods=rest.all)
    rest(Fruit)
    code, json = http.options('/api')
    assert code == 200
    assert json == {
        '/api/fruit': {
            'fields': {
                'age': 'DATETIME',
                'color': 'VARCHAR(50)',
                'fruit_id': 'INTEGER',
                'size': 'NUMERIC',
                'tree_id': 'INTEGER'
            },
            'methods': ['GET']
        },
        '/api/tree': {
            'fields': {'id': 'INTEGER', 'name': 'VARCHAR'},
            'methods': ['GET', 'PUT', 'POST', 'DELETE']
    }}
