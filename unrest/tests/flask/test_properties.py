from . import idsorted
from ..model import Tree


def test_get_tree(rest, http):
    rest(Tree, properties=['fruit_colors'])
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine', 'fruit_colors': 'grey, darkgrey, brown'},
        {'id': 2, 'name': 'maple', 'fruit_colors': 'red, orangered'},
        {'id': 3, 'name': 'oak', 'fruit_colors': ''},
    ]
