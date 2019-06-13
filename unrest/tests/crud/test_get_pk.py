from ...unrest import UnRest
from .. import idsorted
from ..model import Fruit, Tree


def test_get_pk_tree(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree)
    rest(Fruit)
    code, json = client.fetch('/api/tree/1')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [{'id': 1, 'name': 'pine'}]


def test_get_pk_unknown_tree(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree)
    rest(Fruit)
    code, json = client.fetch('/api/tree/6')
    assert code == 200
    assert json['occurences'] == 0
    assert json['objects'] == []


def test_get_pk_tree_name(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, name='forest')
    code, json = client.fetch('/api/forest/2')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [{'id': 2, 'name': 'maple'}]


def test_get_pk_tree_query(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)

    def base_query(q):
        return client.session.query(Tree).filter(Tree.id > 1)

    rest(Tree, query=base_query)
    code, json = client.fetch('/api/tree/2')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [{'id': 2, 'name': 'maple'}]


def test_get_pk_tree_query_not_found(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)

    def base_query(q):
        return client.session.query(Tree).filter(Tree.id > 1)

    rest(Tree, query=base_query)
    code, json = client.fetch('/api/tree/1')
    assert code == 200
    assert json['occurences'] == 0
    assert json['objects'] == []


def test_get_pk_tree_query_factory(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, query=lambda q: q.filter(Tree.id < 2))
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [{'id': 1, 'name': 'pine'}]


def test_get_pk_tree_query_factory_not_found(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, query=lambda q: q.filter(Tree.id < 2))
    code, json = client.fetch('/api/tree/3')
    assert code == 200
    assert json['occurences'] == 0
    assert json['objects'] == []


def test_get_pk_fruits(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree)
    rest(Fruit)
    code, json = client.fetch('/api/fruit/1')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'grey',
            'size': 12.0,
            'double_size': 24.0,
            'age': 1_041_300.0,
            'tree_id': 1,
        }
    ]


def test_get_pk_fruits_only(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, only=['color', 'size'])
    code, json = client.fetch('/api/fruit/2')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {'fruit_id': 2, 'color': 'darkgrey', 'size': 23.0}
    ]


def test_get_pk_fruits_exclude(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, exclude=['color', 'age', 'double_size'])
    code, json = client.fetch('/api/fruit/3')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {'fruit_id': 3, 'size': 2.12, 'tree_id': 1}
    ]


def test_get_pk_fruits_only_exclude(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, only=['color', 'size'], exclude=['color', 'age'])
    code, json = client.fetch('/api/fruit/4')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {'fruit_id': 4, 'size': 0.5}
    ]


def test_no_method(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, methods=[])
    code, html = client.fetch('/api/fruit/1')
    assert code == 404


def test_get_pk_custom(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    fruit = rest(Fruit)

    @fruit.declare('GET')
    def get(payload, fruit_id=None):
        return {'Hey': 'Overridden'}

    assert get is not None

    code, json = client.fetch('/api/fruit/3')
    assert code == 200
    assert json == {'Hey': 'Overridden'}


def test_get_pk_custom_extend(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    fruit = rest(Fruit)

    @fruit.declare('GET')
    def get(payload, fruit_id=None):
        fruit_id += 1
        return fruit.get(payload, fruit_id=fruit_id)

    code, json = client.fetch('/api/fruit/4')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 5,
            'color': 'orangered',
            'size': 100.0,
            'double_size': 200.0,
            'age': 7200.000_012,
            'tree_id': None,
        }
    ]


def test_declare_without_method(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    tree = rest(Tree)

    @tree.declare('POST')
    def post(payload, id=None):
        return {'Hey': 'Overridden'}

    assert post is not None

    code, json = client.fetch(
        '/api/tree', method="POST", json={'name': 'cedar'}
    )
    assert code == 200
    assert json == {'Hey': 'Overridden'}
