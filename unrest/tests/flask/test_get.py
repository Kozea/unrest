from ..model import Tree, Fruit


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
