from . import idsorted
from ..model import Tree


def test_put_tree_implicitly_unallowed(rest, http):
    rest(Tree, methods=['GET', 'PUT'])
    code, json = http.put('/api/tree', json={'id': 1, 'name': 'cedar'})
    assert code == 406


def test_put_tree(rest, http):
    rest(Tree, methods=['GET', 'PUT'], allow_batch=True)
    code, json = http.put('/api/tree', json={
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
    assert json['occurences'] == 2
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'mango'},
    ]
