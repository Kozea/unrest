from . import idsorted
from ..model import Fruit, Tree


def test_get_pk_tree(rest, http):
    rest(Tree)
    rest(Fruit)
    code, json = http.get('/api/tree/1')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'}
    ]


def test_get_pk_unknown_tree(rest, http):
    rest(Tree)
    rest(Fruit)
    code, json = http.get('/api/tree/6')
    assert code == 404
    assert json['message'] == "tree({'id': 6}) not found"


def test_get_pk_tree_name(rest, http):
    rest(Tree, name='forest')
    code, json = http.get('/api/forest/2')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 2, 'name': 'maple'},
    ]


def test_get_pk_tree_query(rest, http, db):
    def base_query(q):
        return db.session.query(Tree).filter(Tree.id > 1)
    rest(Tree, query=base_query)
    code, json = http.get('/api/tree/2')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 2, 'name': 'maple'},
    ]


def test_get_pk_tree_query_not_found(rest, http, db):
    def base_query(q):
        return db.session.query(Tree).filter(Tree.id > 1)
    rest(Tree, query=base_query)
    code, json = http.get('/api/tree/1')
    assert code == 404
    assert json['message'] == "tree({'id': 1}) not found"


def test_get_pk_tree_query_factory(rest, http, db):
    rest(Tree, query=lambda q: q.filter(Tree.id < 2))
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'}
    ]


def test_get_pk_tree_query_factory_not_found(rest, http, db):
    rest(Tree, query=lambda q: q.filter(Tree.id < 2))
    code, json = http.get('/api/tree/3')
    assert code == 404
    assert json['message'] == "tree({'id': 3}) not found"


def test_get_pk_fruits(rest, http):
    rest(Tree)
    rest(Fruit)
    code, json = http.get('/api/fruit/1')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'grey',
            'size': 12.0,
            'age': 1041300.0,
            'tree_id': 1
        }
    ]


def test_get_pk_fruits_only(rest, http):
    rest(Fruit, only=['color', 'size'])
    code, json = http.get('/api/fruit/2')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 2,
            'color': 'darkgrey',
            'size': 23.0
        }
    ]


def test_get_pk_fruits_exclude(rest, http):
    rest(Fruit, exclude=['color', 'age'])
    code, json = http.get('/api/fruit/3')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 3,
            'size': 2.12,
            'tree_id': 1
        }
    ]


def test_get_pk_fruits_only_exclude(rest, http):
    rest(Fruit, only=['color', 'size'], exclude=['color', 'age'])
    code, json = http.get('/api/fruit/4')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 4,
            'size': 0.5
        }
    ]


def test_no_method(rest, http):
    rest(Fruit, methods=[])
    code, json = http.get('/api/fruit/1')
    assert code == 404


def test_get_custom(rest, http):
    fruit = rest(Fruit)

    @fruit.declare('GET')
    def get(payload, fruit_id=None):
        return {'Hey': 'Overridden'}

    code, json = http.get('/api/fruit/3')
    assert code == 200
    assert json == {'Hey': 'Overridden'}


def test_get_custom_extend(rest, http):
    fruit = rest(Fruit)

    @fruit.declare('GET')
    def get(payload, fruit_id=None):
        fruit_id += 1
        return fruit.get(payload, fruit_id=fruit_id)

    code, json = http.get('/api/fruit/4')
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 5,
            'color': 'orangered',
            'size': 100.0,
            'age': 7200.000012,
            'tree_id': 2
        }
    ]
