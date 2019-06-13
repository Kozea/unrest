from ...unrest import UnRest
from .. import idsorted
from ..model import Fruit, Tree


def test_get_tree(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree)
    rest(Fruit)
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]


def test_get_tree_name(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, name='forest')
    code, json = client.fetch('/api/forest')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]


def test_get_tree_query(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)

    def base_query(q):
        return client.session.query(Tree).filter(Tree.id > 1)

    rest(Tree, query=base_query)
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects']) == [
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]


def test_get_tree_query_factory(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, query=lambda q: q.filter(Tree.id < 2))
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 1
    assert json['primary_keys'] == ['id']
    assert idsorted(json['objects']) == [{'id': 1, 'name': 'pine'}]


def test_get_fruits(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree)
    rest(Fruit)
    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert json['primary_keys'] == ['fruit_id']
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'grey',
            'size': 12.0,
            'double_size': 24.0,
            'age': 1_041_300.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 2,
            'color': 'darkgrey',
            'size': 23.0,
            'double_size': 46.0,
            'age': 4_233_830.213,
            'tree_id': 1,
        },
        {
            'fruit_id': 3,
            'color': 'brown',
            'size': 2.12,
            'double_size': 4.24,
            'age': 0.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 4,
            'color': 'red',
            'size': 0.5,
            'double_size': 1.0,
            'age': 2400.0,
            'tree_id': 2,
        },
        {
            'fruit_id': 5,
            'color': 'orangered',
            'size': 100.0,
            'double_size': 200.0,
            'age': 7200.000_012,
            'tree_id': None,
        },
    ]


def test_get_fruits_only(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, only=['color', 'size'])
    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == [
        {'fruit_id': 1, 'color': 'grey', 'size': 12.0},
        {'fruit_id': 2, 'color': 'darkgrey', 'size': 23.0},
        {'fruit_id': 3, 'color': 'brown', 'size': 2.12},
        {'fruit_id': 4, 'color': 'red', 'size': 0.5},
        {'fruit_id': 5, 'color': 'orangered', 'size': 100.0},
    ]


def test_get_fruits_exclude(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, exclude=['color', 'age', 'double_size'])
    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == [
        {'fruit_id': 1, 'size': 12.0, 'tree_id': 1},
        {'fruit_id': 2, 'size': 23.0, 'tree_id': 1},
        {'fruit_id': 3, 'size': 2.12, 'tree_id': 1},
        {'fruit_id': 4, 'size': 0.5, 'tree_id': 2},
        {'fruit_id': 5, 'size': 100.0, 'tree_id': None},
    ]


def test_get_fruits_only_exclude(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, only=['color', 'size'], exclude=['color', 'age'])
    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == [
        {'fruit_id': 1, 'size': 12.0},
        {'fruit_id': 2, 'size': 23.0},
        {'fruit_id': 3, 'size': 2.12},
        {'fruit_id': 4, 'size': 0.5},
        {'fruit_id': 5, 'size': 100.0},
    ]


def test_no_method(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, methods=[])
    code, html = client.fetch('/api/fruit')
    assert code == 404


def test_get_custom(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    fruit = rest(Fruit)

    @fruit.declare('GET')
    def get(payload, fruit_id=None):
        return {'Hey': 'Overridden'}

    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json == {'Hey': 'Overridden'}


def test_get_custom_extend(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    fruit = rest(Fruit)

    @fruit.declare('GET')
    def get(payload, fruit_id=None):
        rv = fruit.get(payload, fruit_id=fruit_id)
        return {
            'occurences': rv['occurences'],
            'objects': [{'id': obj['fruit_id']} for obj in rv['objects']],
        }

    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects']) == [
        {'id': 1},
        {'id': 2},
        {'id': 3},
        {'id': 4},
        {'id': 5},
    ]
