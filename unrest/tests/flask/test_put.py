from . import idsorted
from ..model import Fruit, Tree


def test_put_tree_implicitly_unallowed(rest, http):
    rest(Tree, methods=['GET', 'PUT'])
    code, json = http.put('/api/tree', json={'id': 1, 'name': 'cedar'})
    assert code == 406


def test_put_tree(rest, http):
    rest(Tree, methods=['GET', 'PUT'], allow_batch=True)
    code, json = http.put(
        '/api/tree',
        json={
            'objects': [{
                'id': 1,
                'name': 'cedar'
            }, {
                'id': 2,
                'name': 'mango'
            }]
        }
    )
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects']) == [
        {
            'id': 1,
            'name': 'cedar'
        },
        {
            'id': 2,
            'name': 'mango'
        },
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects']) == [
        {
            'id': 1,
            'name': 'cedar'
        },
        {
            'id': 2,
            'name': 'mango'
        },
    ]


def test_put_with_defaults(rest, http):
    rest(
        Fruit,
        methods=['GET', 'PUT'],
        allow_batch=True,
        defaults={
            'color': 'white',
            'age': lambda p: p['size'] * 2,
        }
    )
    code, json = http.put(
        '/api/fruit',
        json={
            'objects': [{
                'size': 1.0,
                'tree_id': 1
            }, {
                'color': 'yellow',
                'size': 2.0,
                'tree_id': 2
            }]
        }
    )
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'white',
            'size': 1.0,
            'age': 2.0,
            'tree_id': 1
        },
        {
            'fruit_id': 2,
            'color': 'yellow',
            'size': 2.0,
            'age': 4.0,
            'tree_id': 2
        },
    ]

    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'white',
            'size': 1.0,
            'age': 2.0,
            'tree_id': 1
        },
        {
            'fruit_id': 2,
            'color': 'yellow',
            'size': 2.0,
            'age': 4.0,
            'tree_id': 2
        },
    ]


def test_put_with_fixed(rest, http):
    rest(
        Fruit,
        methods=['GET', 'PUT'],
        allow_batch=True,
        fixed={
            'color': 'white',
            'age': lambda p: p['size'] * 2,
        }
    )
    code, json = http.put(
        '/api/fruit',
        json={
            'objects': [{
                'size': 1.0,
                'tree_id': 1
            }, {
                'color': 'yellow',
                'size': 2.0,
                'tree_id': 2
            }]
        }
    )
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'white',
            'size': 1.0,
            'age': 2.0,
            'tree_id': 1
        },
        {
            'fruit_id': 2,
            'color': 'white',
            'size': 2.0,
            'age': 4.0,
            'tree_id': 2
        },
    ]

    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'white',
            'size': 1.0,
            'age': 2.0,
            'tree_id': 1
        },
        {
            'fruit_id': 2,
            'color': 'white',
            'size': 2.0,
            'age': 4.0,
            'tree_id': 2
        },
    ]
