from . import idsorted
from ..model import Tree


def test_post_tree(rest, http):
    rest(Tree, methods=['GET', 'POST'])
    code, json = http.post('/api/tree', json={'name': 'cedar'})
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 4, 'name': 'cedar'},
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 4
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
        {'id': 4, 'name': 'cedar'},
    ]


def test_post_tree_with_id(rest, http):
    rest(Tree, methods=['GET', 'POST'])
    code, json = http.post('/api/tree', json={'id': 9, 'name': 'cedar'})
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 9, 'name': 'cedar'},
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 4
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
        {'id': 9, 'name': 'cedar'},
    ]


def test_post_tree_custom(rest, http):
    tree = rest(Tree)

    @tree.declare('POST')
    def post(payload, id=None):
        payload['name'] = 'I ALWAYS WANT THIS NAME'
        return tree.post(payload, id=id)

    code, json = http.post('/api/tree', json={'name': 'cedar'})
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 4, 'name': 'I ALWAYS WANT THIS NAME'},
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 4
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
        {'id': 4, 'name': 'I ALWAYS WANT THIS NAME'},
    ]
