from sqlalchemy.types import DECIMAL

from . import idsorted
from ..model import Fruit, Tree


def test_get_tree_with_property(rest, http):
    rest(Tree, properties=['fruit_colors'])
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine', 'fruit_colors': 'grey, darkgrey, brown'},
        {'id': 2, 'name': 'maple', 'fruit_colors': 'red, orangered'},
        {'id': 3, 'name': 'oak', 'fruit_colors': ''},
    ]


def test_get_tree_with_object_property(rest, http):
    rest(Tree, properties=[rest.Property('fruit_colors')])
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine', 'fruit_colors': 'grey, darkgrey, brown'},
        {'id': 2, 'name': 'maple', 'fruit_colors': 'red, orangered'},
        {'id': 3, 'name': 'oak', 'fruit_colors': ''},
    ]


results = [
    {'fruit_id': 1, 'color': 'grey', 'size': 12.0,
     'age': 1041300.0, 'tree_id': 1, 'square_size': 144.0},
    {'fruit_id': 2, 'color': 'darkgrey', 'size': 23.0,
     'age': 4233830.213, 'tree_id': 1, 'square_size': 529.0},
    {'fruit_id': 3, 'color': 'brown', 'size': 2.12,
     'age': 0.0, 'tree_id': 1, 'square_size': 4.4944},
    {'fruit_id': 4, 'color': 'red', 'size': 0.5,
     'age': 2400.0, 'tree_id': 2, 'square_size': 0.25},
    {'fruit_id': 5, 'color': 'orangered', 'size': 100.0,
     'age': 7200.000012, 'tree_id': 2, 'square_size': 10000.0}]


def test_get_fruit_with_hybrid_property_and_type(rest, http):
    rest(Fruit, properties=[rest.Property('square_size', DECIMAL())])
    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == results


def test_get_fruit_with_hybrid_property_and_formatter(rest, http):
    rest(Fruit, properties=[rest.Property(
        'square_size', formatter=lambda x: float(x))])
    code, json = http.get('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == results
