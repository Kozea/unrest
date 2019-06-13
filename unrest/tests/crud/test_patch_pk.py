from ...unrest import UnRest
from .. import idsorted
from ..model import Fruit, Tree


def test_patch_tree(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'PATCH'])
    code, json = client.fetch(
        '/api/tree/1', method="PATCH", json={'id': 1, 'name': 'cedar'}
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [{'id': 1, 'name': 'cedar'}]

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]


def test_patch_tree_without_id(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'PATCH'])
    code, json = client.fetch(
        '/api/tree/1', method="PATCH", json={'name': 'cedar'}
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [{'id': 1, 'name': 'cedar'}]

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]


def test_patch_tree_missing_tree(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'PATCH'], allow_batch=True)
    code, json = client.fetch(
        '/api/tree/9',
        method="PATCH",
        json={
            'objects': [{'id': 1, 'name': 'cedar'}, {'id': 8, 'name': 'mango'}]
        },
    )
    assert code == 404
    assert json['message'] == "tree({'id': 9}) not found"


def test_patch_tree_with_another_id(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'PATCH'])
    code, json = client.fetch(
        '/api/tree/1', method="PATCH", json={'id': 5, 'name': 'cedar'}
    )
    assert code == 500


def test_patch_fruit(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, methods=['GET', 'PATCH'], allow_batch=True)
    code, json = client.fetch(
        '/api/fruit/1', method="PATCH", json={'fruit_id': 1, 'color': 'blue'}
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'blue',
            'size': 12.0,
            'double_size': 24.0,
            'age': 1_041_300.0,
            'tree_id': 1,
        }
    ]

    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'blue',
            'size': 12.0,
            'double_size': 24.0,
            'age': 1_041_300.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 2,
            'color': 'darkgrey',
            'size': 23.0,
            'double_size': 46.0,
            'age': 4_233_830.213,
            'tree_id': 1,
        },
        {
            'fruit_id': 3,
            'color': 'brown',
            'size': 2.12,
            'double_size': 4.24,
            'age': 0.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 4,
            'color': 'red',
            'size': 0.5,
            'double_size': 1.0,
            'age': 2400.0,
            'tree_id': 2,
        },
        {
            'fruit_id': 5,
            'color': 'orangered',
            'size': 100.0,
            'double_size': 200.0,
            'age': 7200.000_012,
            'tree_id': None,
        },
    ]
