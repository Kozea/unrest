from . import idsorted
from ..model import Tree


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
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 0
    assert idsorted(json['objects']) == []
