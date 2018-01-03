from . import idsorted
from ..model import Fruit, Tree


def test_post_tree(rest, http):
    rest(Tree, methods=['GET', 'POST'])
    code, json = http.post('/api/tree', json={'name': 'cedar'})
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {
            'id': 4,
            'name': 'cedar'
        },
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 4
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
        {
            'id': 4,
            'name': 'cedar'
        },
    ]


def test_post_tree_with_id(rest, http):
    rest(Tree, methods=['GET', 'POST'])
    code, json = http.post('/api/tree', json={'id': 9, 'name': 'cedar'})
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {
            'id': 9,
            'name': 'cedar'
        },
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 4
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
        {
            'id': 9,
            'name': 'cedar'
        },
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
        {
            'id': 4,
            'name': 'I ALWAYS WANT THIS NAME'
        },
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 4
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
        {
            'id': 4,
            'name': 'I ALWAYS WANT THIS NAME'
        },
    ]


def test_post_tree_custom_manual_commit(rest, http):
    tree = rest(Tree)

    @tree.declare('POST', True)
    def post(payload, id=None):
        payload['name'] = 'I ALWAYS WANT THIS NAME'
        return tree.post(payload, id=id)

    code, json = http.post('/api/tree', json={'name': 'cedar'})
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {
            'id': 4,
            'name': 'I ALWAYS WANT THIS NAME'
        },
    ]
    # The post should not be commited
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [{
        'id': 1,
        'name': 'pine'
    }, {
        'id': 2,
        'name': 'maple'
    }, {
        'id': 3,
        'name': 'oak'
    }]


def test_post_with_defaults(rest, http):
    rest(
        Fruit,
        methods=['GET', 'POST'],
        defaults={
            'color': 'white',
            'age': lambda p: p['size'] * 2,
        }
    )
    code, json = http.post('/api/fruit', json={'size': 1.0, 'tree_id': 1})
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 6,
            'color': 'white',
            'size': 1.0,
            'age': 2.0,
            'tree_id': 1
        },
    ]
    code, json = http.post(
        '/api/fruit', json={
            'color': 'yellow',
            'size': 2.0,
            'tree_id': 2
        }
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 7,
            'color': 'yellow',
            'size': 2.0,
            'age': 4.0,
            'tree_id': 2
        },
    ]

    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 7
    assert idsorted(json['objects'][-2:], 'fruit_id') == [
        {
            'fruit_id': 6,
            'color': 'white',
            'size': 1.0,
            'age': 2.0,
            'tree_id': 1
        },
        {
            'fruit_id': 7,
            'color': 'yellow',
            'size': 2.0,
            'age': 4.0,
            'tree_id': 2
        },
    ]


def test_post_with_fixed(rest, http):
    rest(
        Fruit,
        methods=['GET', 'POST'],
        fixed={
            'color': 'white',
            'age': lambda p: p['size'] * 2,
        }
    )
    code, json = http.post('/api/fruit', json={'size': 1.0, 'tree_id': 1})
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 6,
            'color': 'white',
            'size': 1.0,
            'age': 2.0,
            'tree_id': 1
        },
    ]
    code, json = http.post(
        '/api/fruit', json={
            'color': 'yellow',
            'size': 2.0,
            'tree_id': 2
        }
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 7,
            'color': 'white',
            'size': 2.0,
            'age': 4.0,
            'tree_id': 2
        },
    ]

    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 7
    assert idsorted(json['objects'][-2:], 'fruit_id') == [
        {
            'fruit_id': 6,
            'color': 'white',
            'size': 1.0,
            'age': 2.0,
            'tree_id': 1
        },
        {
            'fruit_id': 7,
            'color': 'white',
            'size': 2.0,
            'age': 4.0,
            'tree_id': 2
        },
    ]
