from . import idsorted
from ..model import Tree


def test_put_tree(rest, http):
    rest(Tree, methods=['GET', 'PUT'])
    code, json = http.put('/api/tree/1', json={'id': 1, 'name': 'cedar'})
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


def test_put_tree_without_id(rest, http):
    rest(Tree, methods=['GET', 'PUT'])
    code, json = http.put('/api/tree/1', json={'name': 'cedar'})
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


def test_put_tree_with_another_id(rest, http):
    rest(Tree, methods=['GET', 'PUT'])
    code, json = http.put('/api/tree/1', json={'id': 5, 'name': 'cedar'})
    assert code == 500
