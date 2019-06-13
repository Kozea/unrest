from ...unrest import UnRest
from .. import idsorted
from ..model import Fruit, Tree


def test_post_tree(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'POST'])
    code, json = client.fetch(
        '/api/tree', method="POST", json={'name': 'cedar'}
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [{'id': 4, 'name': 'cedar'}]

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 4
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
        {'id': 4, 'name': 'cedar'},
    ]


def test_post_tree_null_value(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'POST'])
    code, json = client.fetch('/api/tree', method="POST", json={'name': None})
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [{'id': 4, 'name': None}]

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 4
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
        {'id': 4, 'name': None},
    ]


def test_post_empty_payload(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'POST'])
    code, json = client.fetch('/api/tree', method="POST", json={})
    assert code == 400
    assert json['message'] == 'You must provide a payload'


def test_post_tree_with_id(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'POST'])
    code, json = client.fetch(
        '/api/tree', method="POST", json={'id': 9, 'name': 'cedar'}
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [{'id': 9, 'name': 'cedar'}]

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 4
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
        {'id': 9, 'name': 'cedar'},
    ]


def test_post_tree_custom(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    tree = rest(Tree)

    @tree.declare('POST')
    def post(payload, id=None):
        payload['name'] = 'I ALWAYS WANT THIS NAME'
        return tree.post(payload, id=id)

    code, json = client.fetch(
        '/api/tree', method="POST", json={'name': 'cedar'}
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 4, 'name': 'I ALWAYS WANT THIS NAME'}
    ]

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 4
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
        {'id': 4, 'name': 'I ALWAYS WANT THIS NAME'},
    ]


def test_post_tree_custom_manual_commit(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    tree = rest(Tree)

    @tree.declare('POST', True)
    def post(payload, id=None):
        payload['name'] = 'I ALWAYS WANT THIS NAME'
        return tree.post(payload, id=id)

    code, json = client.fetch(
        '/api/tree', method="POST", json={'name': 'cedar'}
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 4, 'name': 'I ALWAYS WANT THIS NAME'}
    ]
    # The post should not be commited
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]


def test_post_with_defaults(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(
        Fruit,
        methods=['GET', 'POST'],
        defaults={'color': 'white', 'age': lambda p: p['size'] * 2},
    )
    code, json = client.fetch(
        '/api/fruit', method="POST", json={'size': 1.0, 'tree_id': 1}
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 6,
            'color': 'white',
            'size': 1.0,
            'double_size': 2.0,
            'age': 2.0,
            'tree_id': 1,
        }
    ]
    code, json = client.fetch(
        '/api/fruit',
        method="POST",
        json={'color': 'yellow', 'size': 2.0, 'tree_id': 2},
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 7,
            'color': 'yellow',
            'size': 2.0,
            'double_size': 4.0,
            'age': 4.0,
            'tree_id': 2,
        }
    ]

    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 7
    assert idsorted(json['objects'][-2:], 'fruit_id') == [
        {
            'fruit_id': 6,
            'color': 'white',
            'size': 1.0,
            'double_size': 2.0,
            'age': 2.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 7,
            'color': 'yellow',
            'size': 2.0,
            'double_size': 4.0,
            'age': 4.0,
            'tree_id': 2,
        },
    ]


def test_post_with_fixed(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(
        Fruit,
        methods=['GET', 'POST'],
        fixed={'color': 'white', 'age': lambda p: p['size'] * 2},
    )
    code, json = client.fetch(
        '/api/fruit', method="POST", json={'size': 1.0, 'tree_id': 1}
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 6,
            'color': 'white',
            'size': 1.0,
            'double_size': 2.0,
            'age': 2.0,
            'tree_id': 1,
        }
    ]
    code, json = client.fetch(
        '/api/fruit',
        method="POST",
        json={'color': 'yellow', 'size': 2.0, 'tree_id': 2},
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 7,
            'color': 'white',
            'size': 2.0,
            'double_size': 4.0,
            'age': 4.0,
            'tree_id': 2,
        }
    ]

    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 7
    assert idsorted(json['objects'][-2:], 'fruit_id') == [
        {
            'fruit_id': 6,
            'color': 'white',
            'size': 1.0,
            'double_size': 2.0,
            'age': 2.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 7,
            'color': 'white',
            'size': 2.0,
            'double_size': 4.0,
            'age': 4.0,
            'tree_id': 2,
        },
    ]
