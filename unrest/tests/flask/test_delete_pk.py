from . import idsorted
from ..model import Tree


def test_delete_tree(rest, http):
    rest(Tree, methods=['GET', 'DELETE'])
    code, json = http.delete('/api/tree/2')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 2, 'name': 'maple'},
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 3, 'name': 'oak'},
    ]


def test_delete_unknown_tree(rest, http):
    rest(Tree, methods=['DELETE'])
    code, json = http.delete('/api/tree/9')
    assert code == 404
