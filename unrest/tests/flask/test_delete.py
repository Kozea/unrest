from . import idsorted
from ..model import Fruit, Tree


def test_delete_tree_implicitly_unallowed(rest, http):
    rest(Tree, methods=['GET', 'DELETE'])
    code, json = http.delete('/api/tree')
    assert code == 406


def test_delete_tree(rest, http):
    rest(Tree, methods=['GET', 'DELETE'], allow_batch=True)
    code, json = http.delete('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {
            'id': 1,
            'name': 'pine'
        },
        {
            'id': 2,
            'name': 'maple'
        },
        {
            'id': 3,
            'name': 'oak'
        },
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 0
    assert idsorted(json['objects']) == []


def test_delete_fruits(rest, http):
    rest(Fruit, methods=['GET', 'DELETE'], allow_batch=True)
    code, json = http.delete('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == [{
        'fruit_id': 1,
        'color': 'grey',
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
    }]

    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 0
    assert idsorted(json['objects']) == []
