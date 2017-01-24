from ..model import Fruit, Tree


def idsorted(it, key='id'):
    return sorted(it, key=lambda x: x[key])


def test_get_tree(rest, http):
    rest(Tree)
    rest(Fruit)
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]


def test_get_fruits(rest, http):
    rest(Tree)
    rest(Fruit)
    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'grey',
            'size': 12.0,
            'age': 1041300.0,
            'tree_id': 1
        }, {
            'fruit_id': 2,
            'color': 'darkgrey',
            'size': 23.0,
            'age': 4233830.213,
            'tree_id': 1
        }, {
            'fruit_id': 3,
            'color': 'brown',
            'size': 2.12,
            'age': 0.0,
            'tree_id': 1
        }, {
            'fruit_id': 4,
            'color': 'red',
            'size': 0.5,
            'age': 2400.0,
            'tree_id': 2
        }, {
            'fruit_id': 5,
            'color': 'orangered',
            'size': 100.0,
            'age': 7200.000012,
            'tree_id': 2
        }
    ]


def test_get_fruits_only(rest, http):
    rest(Fruit, only=['color', 'size'])
    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'grey',
            'size': 12.0
        }, {
            'fruit_id': 2,
            'color': 'darkgrey',
            'size': 23.0
        }, {
            'fruit_id': 3,
            'color': 'brown',
            'size': 2.12
        }, {
            'fruit_id': 4,
            'color': 'red',
            'size': 0.5
        }, {
            'fruit_id': 5,
            'color': 'orangered',
            'size': 100.0
        }
    ]


def test_get_fruits_exclude(rest, http):
    rest(Fruit, exclude=['color', 'age'])
    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'size': 12.0,
            'tree_id': 1
        }, {
            'fruit_id': 2,
            'size': 23.0,
            'tree_id': 1
        }, {
            'fruit_id': 3,
            'size': 2.12,
            'tree_id': 1
        }, {
            'fruit_id': 4,
            'size': 0.5,
            'tree_id': 2
        }, {
            'fruit_id': 5,
            'size': 100.0,
            'tree_id': 2
        }
    ]


def test_get_fruits_only_exclude(rest, http):
    rest(Fruit, only=['color', 'size'], exclude=['color', 'age'])
    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 1,
            'size': 12.0
        }, {
            'fruit_id': 2,
            'size': 23.0
        }, {
            'fruit_id': 3,
            'size': 2.12
        }, {
            'fruit_id': 4,
            'size': 0.5
        }, {
            'fruit_id': 5,
            'size': 100.0
        }
    ]
