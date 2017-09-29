from . import idsorted
from ..model import Fruit, Tree


def test_delete_tree(rest, http):
    rest(Tree, methods=['GET', 'DELETE'])
    code, json = http.delete('/api/tree/2')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {
            'id': 2,
            'name': 'maple'
        },
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects']) == [
        {
            'id': 1,
            'name': 'pine'
        },
        {
            'id': 3,
            'name': 'oak'
        },
    ]


def test_delete_unknown_tree(rest, http):
    rest(Tree, methods=['DELETE'])
    code, json = http.delete('/api/tree/9')
    assert code == 404


def test_delete_fruit(rest, http):
    rest(Fruit, methods=['GET', 'DELETE'])
    code, json = http.delete('/api/fruit/2')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 2,
            'color': 'darkgrey',
            'size': 23.0,
            'age': 4233830.213,
            'tree_id': 1
        },
    ]

    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 4
    assert idsorted(json['objects'], 'fruit_id') == [{
        'fruit_id': 1,
        'color': 'grey',
        'size': 12.0,
        'age': 1041300.0,
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
