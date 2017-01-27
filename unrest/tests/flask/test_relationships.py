from . import idsorted
from ..model import Fruit, Tree


def test_get_tree_with_relationship(rest, http):
    fruit = rest(Fruit, methods=[], only=['color'])

    rest(Tree, relationships={'fruits': fruit})
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine', 'fruits': [
            {'fruit_id': 1, 'color': 'grey'},
            {'fruit_id': 2, 'color': 'darkgrey'},
            {'fruit_id': 3, 'color': 'brown'}
        ]},
        {'id': 2, 'name': 'maple', 'fruits': [
            {'fruit_id': 4, 'color': 'red'},
            {'fruit_id': 5, 'color': 'orangered'}
        ]},
        {'id': 3, 'name': 'oak', 'fruits': []},
    ]
    code, json = http.get('/api/fruit')
    assert code == 404
