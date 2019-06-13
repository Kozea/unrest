import sys

from pytest import raises
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.types import Boolean, Float, String

from unrest import UnRest, __about__
from unrest.coercers import Deserialize, Serialize
from unrest.rest import Rest

from ...framework import Framework
from ...framework.flask import FlaskFramework
from .. import idsorted
from ..model import Fruit, Tree
from ..static.openapi_result import openapi


def test_other_url(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree)
    code, html = client.fetch('/')
    assert code == 200
    assert html == 'A normal route!'


def test_index(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree)
    code, html = client.fetch('/api/')
    assert code == 200
    assert html == (
        '<h1>unrest <small>api server</small></h1> version '
        f'{__about__.__version__} '
        '<a href="https://github.com/Kozea/unrest">unrest</a> '
        '<a href="/api/openapi.json">openapi.json</a>'
    )


def test_normal(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree)
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 3


def test_path(client):
    rest = UnRest(
        client.app, client.session, '/forest', framework=client.__framework__
    )
    rest(Tree)
    code, json = client.fetch('/forest/tree')
    assert code == 200
    assert json['occurences'] == 3


def test_schema(client):
    Tree.__table__.schema = 'forest'

    def reset_schema(query):
        Tree.__table__.schema = None
        return query

    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, query=reset_schema)
    code, json = client.fetch('/api/forest/tree')
    assert code == 200
    assert json['occurences'] == 3


def test_version(client):
    rest = UnRest(
        client.app,
        client.session,
        version='v3.14',
        framework=client.__framework__,
    )
    rest(Tree)
    code, json = client.fetch('/api/v3.14/tree')
    assert code == 200
    assert json['occurences'] == 3


def test_path_and_version(client):
    rest = UnRest(
        client.app,
        client.session,
        '/forest',
        'v3.14',
        framework=client.__framework__,
    )
    rest(Tree)
    code, json = client.fetch('/forest/v3.14/tree')
    assert code == 200
    assert json['occurences'] == 3


def test_normal_rest_class(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    tree = rest(Tree, name='tree')
    assert isinstance(tree, Rest)


def test_alternative_rest_class(client):
    class NewRest(Rest):
        def __init__(client, *args, **kwargs):
            kwargs['name'] = 'new_' + kwargs['name']
            super().__init__(*args, **kwargs)

    new_rest = UnRest(
        client.app,
        client.session,
        framework=client.__framework__,
        RestClass=NewRest,
    )
    new_tree = new_rest(Tree, name='tree')
    assert isinstance(new_tree, NewRest)

    code, json = client.fetch('/api/tree')
    assert code == 404
    code, json = client.fetch('/api/new_tree')
    assert code == 200
    assert json['occurences'] == 3


def test_empty_get_pk_as_404(client):
    rest = UnRest(
        client.app,
        client.session,
        framework=client.__framework__,
        empty_get_as_404=True,
    )
    rest(Tree)
    code, json = client.fetch('/api/tree/6')
    assert code == 404
    assert json['occurences'] == 0
    assert json['objects'] == []


def test_bad_json(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'POST'])
    code, json = client.fetch(
        '/api/tree', method="POST", body="{'name'; 'cedar'}"
    )
    assert code == 400
    assert (
        json['message'] == 'JSON Error in payload: '
        'Expecting property name enclosed in double quotes: '
        'line 1 column 2 (char 1)'
    )


def test_empty_explicit_framework(client):
    class FakeUnRest(object):
        def __init__(client, app, url):
            pass

        def register_route(client, *args, **kwargs):
            pass

    rest = UnRest(client.app, client.session, framework=FakeUnRest)
    rest(Tree)
    code, _ = client.fetch('/api/tree')
    assert code == 404


def test_api_options(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    fruit = rest(Fruit)
    rest(
        Tree,
        methods=rest.all,
        relationships={'fruits': fruit},
        properties=['fruit_colors'],
        allow_batch=True,
    )
    code, json = client.fetch('/api', method="OPTIONS")
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
                'tree_id': 'int',
                'double_size': 'Decimal',
            },
            'properties': {},
            'relationships': {},
            'methods': ['GET', 'OPTIONS'],
            'batch': False,
        },
        '/api/tree': {
            'model': 'Tree',
            'description': "Where money doesn't grow",
            'parameters': ['id'],
            'columns': {'id': 'int', 'name': 'str'},
            'properties': {'fruit_colors': 'str'},
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
                        'tree_id': 'int',
                        'double_size': 'Decimal',
                    },
                    'properties': {},
                    'relationships': {},
                    'batch': False,
                }
            },
            'methods': ['GET', 'PUT', 'POST', 'DELETE', 'PATCH', 'OPTIONS'],
            'batch': True,
        },
    }


def test_endpoint_options(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    fruit = rest(Fruit)
    rest(
        Tree,
        methods=rest.all,
        relationships={'fruits': fruit},
        properties=['fruit_colors'],
        allow_batch=True,
    )
    code, json = client.fetch('/api/fruit', method="OPTIONS")
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
            'tree_id': 'int',
            'double_size': 'Decimal',
        },
        'properties': {},
        'relationships': {},
        'methods': ['GET', 'OPTIONS'],
    }


def test_endpoint_options_other_type(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(
        Tree,
        properties=[
            rest.Property('fake_prop_1', type=Boolean()),
            rest.Property('fake_prop_2', type=INET()),
        ],
    )
    code, json = client.fetch('/api/tree', method="OPTIONS")
    assert code == 200
    assert {
        'model': 'Tree',
        'description': "Where money doesn't grow",
        'parameters': ['id'],
        'columns': {'id': 'int', 'name': 'str'},
        'properties': {'fake_prop_1': 'bool', 'fake_prop_2': 'INET'},
        'relationships': {},
        'methods': ['GET', 'OPTIONS'],
        'batch': False,
    }


def test_endpoint_options_no_methods(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=[])
    code, json = client.fetch('/api/tree', method="OPTIONS")
    assert code == 404


def test_endpoint_options_no_methods_but_declare(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    tree = rest(Tree, methods=[])

    @tree.declare('GET')
    def get(payload, id=None):
        return {'Hey': 'Overridden'}

    @tree.declare('POST')
    def post(payload, id=None):
        return {'Hey': 'Overridden'}

    code, json = client.fetch('/api/tree', method="GET")
    assert code == 200
    code, json = client.fetch('/api/tree', method="POST", json={})
    assert code == 200

    code, json = client.fetch('/api/tree', method="OPTIONS")
    assert code == 200


def test_openapi(client):
    rest = UnRest(
        client.app,
        client.session,
        info={
            'description': '''# Unrest demo
This is the demo of unrest api.
This api expose the `Tree` and `Fruit` entity Rest methods.
''',
            'contact': {
                'name': __about__.__author__,
                'url': __about__.__uri__,
                'email': __about__.__email__,
            },
            'license': {'name': __about__.__license__},
        },
        framework=client.__framework__,
    )
    fruit = rest(
        Fruit,
        methods=rest.all,
        properties=[rest.Property('square_size', Float())],
    )
    rest(
        Tree,
        methods=rest.all,
        relationships={'fruits': fruit},
        properties=['fruit_colors'],
        allow_batch=True,
    )
    code, json = client.fetch('/api/openapi.json')
    # Only flask supports absolute url
    if 'Flask' not in client.__framework__.__name__:
        res = {**openapi, 'servers': [{'url': '/api'}]}
    else:
        res = openapi
    assert code == 200
    assert json == res


def test_openapi_other_type(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(
        Tree,
        properties=[
            rest.Property('fake_prop_1', type=Boolean()),
            rest.Property('fake_prop_2', type=INET()),
        ],
    )
    code, json = client.fetch('/api/openapi.json')
    assert code == 200
    assert json['paths']['/tree']['get']['responses']['200']['content'][
        'application/json'
    ]['schema']['properties']['objects']['items']['properties'] == {
        'fake_prop_1': {'type': 'boolean'},
        'fake_prop_2': {'type': 'string'},
        'id': {'format': 'int64', 'type': 'integer'},
        'name': {'type': 'string'},
    }


def test_sub(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)

    fruit = rest(
        Fruit,
        methods=rest.all,
        properties=[rest.Property('square_size', Float())],
    )
    tree = rest(
        Tree,
        methods=rest.all,
        relationships={'fruits': fruit},
        properties=['fruit_colors'],
        query=lambda q: q.filter(Tree.name != 'pine'),
        allow_batch=True,
    )
    subtree = tree.sub(lambda q: q.filter(Tree.name != 'oak'))
    for key in [
        'unrest',
        'Model',
        'methods',
        'only',
        'exclude',
        'properties',
        'relationships',
        'allow_batch',
        'auth',
        'read_auth',
        'write_auth',
        'validators',
        '_primary_keys',
        'SerializeClass',
        'DeserializeClass',
    ]:
        assert getattr(subtree, key) == getattr(tree, key)
    assert subtree.name == 'subtree'

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 2

    code, json = client.fetch('/api/subtree')
    assert code == 200
    assert json['occurences'] == 1

    subtree = tree.sub(
        lambda q: q.filter(Tree.name != 'maple'), name='nomaple'
    )
    code, json = client.fetch('/api/nomaple')
    assert code == 200
    assert json['occurences'] == 1


def test_sub_fixed(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)

    fruit = rest(
        Fruit,
        defaults={'size': 1.0},
        fixed={'color': 'blue'},
        methods=rest.all,
        properties=[rest.Property('square_size', Float())],
    )
    subfruit = fruit.sub(lambda q: q.filter(Fruit.age == 2.0))
    for key in ['defaults', 'fixed']:
        assert getattr(subfruit, key) == getattr(fruit, key)


def test_wrong_framework(client):
    with raises(NotImplementedError):
        UnRest(client.app, client.session, framework=Framework)


def test_auto_framework(client):
    if 'Flask' not in client.__framework__.__name__:
        return
    rest = UnRest(client.app, client.session)
    assert isinstance(rest.framework, FlaskFramework)


def test_no_framework(client):
    if 'Flask' not in client.__framework__.__name__:
        return
    flask = sys.modules['flask']
    sys.modules['flask'] = None

    with raises(NotImplementedError):
        UnRest(client.app, client.session)

    sys.modules['flask'] = flask


def test_custom_serialization(client):
    class UpperCaseStringSerialize(Serialize):
        def serialize(client, name, column):
            rv = super().serialize(name, column)
            if isinstance(column.type, String):
                return rv.upper()
            return rv

    rest = UnRest(
        client.app,
        client.session,
        SerializeClass=UpperCaseStringSerialize,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'PUT'])

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'PINE'},
        {'id': 2, 'name': 'MAPLE'},
        {'id': 3, 'name': 'OAK'},
    ]


def test_custom_deserialization(client):
    class UpperCaseStringDeserialize(Deserialize):
        def deserialize(client, name, column, payload=None):
            rv = super().deserialize(name, column, payload)
            if isinstance(column.type, String):
                return rv.upper()
            return rv

    rest = UnRest(
        client.app,
        client.session,
        DeserializeClass=UpperCaseStringDeserialize,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'PUT'])

    code, json = client.fetch(
        '/api/tree/1', method="PUT", json={'id': 1, 'name': 'cedar'}
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [{'id': 1, 'name': 'CEDAR'}]

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'CEDAR'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]


def test_wrong_method(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'POST'])
    code, html = client.fetch(
        '/api/tree',
        method="PUT",
        json={
            'objects': [{'id': 1, 'name': 'cedar'}, {'id': 2, 'name': 'mango'}]
        },
    )
    assert code == 405


def test_wrong_url(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree)
    code, html = client.fetch('/apy/trea')
    assert code == 404


def test_duplicate_rest(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree)

    with raises(Exception):
        rest(Tree)
