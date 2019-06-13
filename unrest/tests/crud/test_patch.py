from datetime import timedelta

from ...unrest import UnRest
from .. import idsorted
from ..model import Fruit, Tree


def test_patch_tree_implicitly_unallowed(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'PATCH'])
    code, json = client.fetch(
        '/api/tree', method="PATCH", json={'id': 1, 'name': 'cedar'}
    )
    assert code == 406


def test_patch_empty_payload(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'PATCH'])
    code, json = client.fetch('/api/tree', method="PATCH", json={})
    assert code == 400
    assert json['message'] == 'You must provide a payload'


def test_patch_tree(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'PATCH'], allow_batch=True)
    code, json = client.fetch(
        '/api/tree',
        method="PATCH",
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
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'mango'},
        {'id': 3, 'name': 'oak'},
    ]


def test_patch_missing_tree(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'PATCH'], allow_batch=True)
    code, json = client.fetch(
        '/api/tree',
        method="PATCH",
        json={
            'objects': [{'id': 1, 'name': 'cedar'}, {'id': 8, 'name': 'mango'}]
        },
    )
    assert code == 404


def test_patch_fruit(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, methods=['GET', 'PATCH'], allow_batch=True)
    code, json = client.fetch(
        '/api/fruit',
        method="PATCH",
        json={
            'objects': [
                {'fruit_id': 1, 'color': 'blue'},
                {
                    'fruit_id': 3,
                    'age': timedelta(days=12, minutes=29).total_seconds(),
                },
                {'fruit_id': 4, 'color': 'rainbow', 'size': 8},
                {'fruit_id': 5, 'size': 10, 'tree_id': 1},
            ]
        },
    )
    assert code == 200
    assert json['occurences'] == 4
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
            'fruit_id': 3,
            'color': 'brown',
            'size': 2.12,
            'double_size': 4.24,
            'age': 1_038_540.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 4,
            'color': 'rainbow',
            'size': 8.0,
            'double_size': 16.0,
            'age': 2400.0,
            'tree_id': 2,
        },
        {
            'fruit_id': 5,
            'color': 'orangered',
            'size': 10.0,
            'double_size': 20.0,
            'age': 7200.000_012,
            'tree_id': 1,
        },
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
            'age': 1_038_540.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 4,
            'color': 'rainbow',
            'size': 8.0,
            'double_size': 16.0,
            'age': 2400.0,
            'tree_id': 2,
        },
        {
            'fruit_id': 5,
            'color': 'orangered',
            'size': 10.0,
            'double_size': 20.0,
            'age': 7200.000_012,
            'tree_id': 1,
        },
    ]
