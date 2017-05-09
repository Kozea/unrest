from . import idsorted
from ..model import Fruit, Tree


def test_patch_tree(rest, http):
    rest(Tree, methods=['GET', 'PATCH'])
    code, json = http.patch('/api/tree/1', json={'id': 1, 'name': 'cedar'})
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'cedar'},
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]


def test_patch_tree_without_id(rest, http):
    rest(Tree, methods=['GET', 'PATCH'])
    code, json = http.patch('/api/tree/1', json={'name': 'cedar'})
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'cedar'},
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]


def test_patch_tree_with_another_id(rest, http):
    rest(Tree, methods=['GET', 'PATCH'])
    code, json = http.patch('/api/tree/1', json={'id': 5, 'name': 'cedar'})
    assert code == 500


def test_patch_fruit(rest, http):
    rest(Fruit, methods=['GET', 'PATCH'], allow_batch=True)
    code, json = http.patch('/api/fruit/1', json={
        'fruit_id': 1, 'color': 'blue'
    })
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'blue',
            'size': 12.0,
            'age': 1041300.0,
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
            'age': 0.0,
            'tree_id': 1
        }, {
            'fruit_id': 4,
            'color': 'red',
            'size': 0.5,
            'age': 2400.0,
            'tree_id': 2
        }, {
            'fruit_id': 5,
            'color': 'orangered',
            'size': 100.0,
            'age': 7200.000012,
            'tree_id': 2
        }
    ]
