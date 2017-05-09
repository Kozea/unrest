from datetime import timedelta

from . import idsorted
from ..model import Fruit, Tree


def test_patch_tree_implicitly_unallowed(rest, http):
    rest(Tree, methods=['GET', 'PATCH'])
    code, json = http.patch('/api/tree', json={'id': 1, 'name': 'cedar'})
    assert code == 406


def test_patch_tree(rest, http):
    rest(Tree, methods=['GET', 'PATCH'], allow_batch=True)
    code, json = http.patch('/api/tree', json={
        'objects': [
            {'id': 1, 'name': 'cedar'}, {'id': 2, 'name': 'mango'}
        ]})
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'mango'},
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'mango'},
        {'id': 3, 'name': 'oak'},
    ]


def test_patch_missing_tree(rest, http):
    rest(Tree, methods=['GET', 'PATCH'], allow_batch=True)
    code, json = http.patch('/api/tree', json={
        'objects': [
            {'id': 1, 'name': 'cedar'}, {'id': 8, 'name': 'mango'}
        ]})
    assert code == 404


def test_patch_fruit(rest, http):
    rest(Fruit, methods=['GET', 'PATCH'], allow_batch=True)
    code, json = http.patch('/api/fruit', json={
        'objects': [
            {'fruit_id': 1, 'color': 'blue'},
            {'fruit_id': 3, 'age': timedelta(days=12, minutes=29)
             .total_seconds()},
            {'fruit_id': 4, 'color': 'rainbow', 'size': 8},
            {'fruit_id': 5, 'size': 10, 'tree_id': 1},
        ]})
    assert code == 200
    assert json['occurences'] == 4
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'blue',
            'size': 12.0,
            'age': 1041300.0,
            'tree_id': 1
        }, {
            'fruit_id': 3,
            'color': 'brown',
            'size': 2.12,
            'age': 1038540.0,
            'tree_id': 1
        }, {
            'fruit_id': 4,
            'color': 'rainbow',
            'size': 8.0,
            'age': 2400.0,
            'tree_id': 2
        }, {
            'fruit_id': 5,
            'color': 'orangered',
            'size': 10.0,
            'age': 7200.000012,
            'tree_id': 1
        }
    ]

    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'blue',
            'size': 12.0,
            'age': 1041300.0,
            'tree_id': 1
        }, {
            'fruit_id': 2,
            'color': 'darkgrey',
            'size': 23.0,
            'age': 4233830.213,
            'tree_id': 1
        }, {
            'fruit_id': 3,
            'color': 'brown',
            'size': 2.12,
            'age': 1038540.0,
            'tree_id': 1
        }, {
            'fruit_id': 4,
            'color': 'rainbow',
            'size': 8.0,
            'age': 2400.0,
            'tree_id': 2
        }, {
            'fruit_id': 5,
            'color': 'orangered',
            'size': 10.0,
            'age': 7200.000012,
            'tree_id': 1
        }
    ]
