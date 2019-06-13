from ...unrest import UnRest
from .. import idsorted
from ..model import Fruit, Tree


def test_put_tree_implicitly_unallowed(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'PUT'])
    code, html = client.fetch(
        '/api/tree', method="PUT", json={'id': 1, 'name': 'cedar'}
    )
    assert code == 406


def test_put_empty_payload(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'PUT'])
    code, json = client.fetch('/api/tree', method="PUT", json={})
    assert code == 400
    assert json['message'] == 'You must provide a payload'


def test_put_tree(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'PUT'], allow_batch=True)
    code, json = client.fetch(
        '/api/tree',
        method="PUT",
        json={
            'objects': [{'id': 1, 'name': 'cedar'}, {'id': 2, 'name': 'mango'}]
        },
    )
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'mango'},
    ]

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'mango'},
    ]


def test_put_with_defaults(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(
        Fruit,
        methods=['GET', 'PUT'],
        allow_batch=True,
        defaults={'color': 'white', 'age': lambda p: p['size'] * 2},
    )
    code, json = client.fetch(
        '/api/fruit',
        method="PUT",
        json={
            'objects': [
                {'size': 1.0, 'tree_id': 1},
                {'color': 'yellow', 'size': 2.0, 'tree_id': 2},
            ]
        },
    )
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'white',
            'size': 1.0,
            'double_size': 2.0,
            'age': 2.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 2,
            'color': 'yellow',
            'size': 2.0,
            'double_size': 4.0,
            'age': 4.0,
            'tree_id': 2,
        },
    ]

    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'white',
            'size': 1.0,
            'double_size': 2.0,
            'age': 2.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 2,
            'color': 'yellow',
            'size': 2.0,
            'double_size': 4.0,
            'age': 4.0,
            'tree_id': 2,
        },
    ]


def test_put_with_fixed(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(
        Fruit,
        methods=['GET', 'PUT'],
        allow_batch=True,
        fixed={'color': 'white', 'age': lambda p: p['size'] * 2},
    )
    code, json = client.fetch(
        '/api/fruit',
        method="PUT",
        json={
            'objects': [
                {'size': 1.0, 'tree_id': 1},
                {'color': 'yellow', 'size': 2.0, 'tree_id': 2},
            ]
        },
    )
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'white',
            'size': 1.0,
            'double_size': 2.0,
            'age': 2.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 2,
            'color': 'white',
            'size': 2.0,
            'double_size': 4.0,
            'age': 4.0,
            'tree_id': 2,
        },
    ]

    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'white',
            'size': 1.0,
            'double_size': 2.0,
            'age': 2.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 2,
            'color': 'white',
            'size': 2.0,
            'double_size': 4.0,
            'age': 4.0,
            'tree_id': 2,
        },
    ]
