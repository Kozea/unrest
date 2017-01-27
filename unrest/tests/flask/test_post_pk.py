from . import idsorted
from ..model import Tree


def test_post_tree_with_pk(rest, http):
    rest(Tree, methods=['GET', 'POST'])
    code, json = http.post('/api/tree/6', json={'name': 'mango'})
    assert code == 501


def test_post_tree_with_pk_custom(rest, http):
    tree = rest(Tree)

    @tree.declare('POST')
    def post(payload, id=None):
        # Make it work anyway
        return tree.post(payload)

    code, json = http.post('/api/tree/9', json={'name': 'mango'})
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 4, 'name': 'mango'},
    ]

    code, json = http.get('/api/tree')
    assert json['occurences'] == 4
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
        {'id': 4, 'name': 'mango'},
    ]
