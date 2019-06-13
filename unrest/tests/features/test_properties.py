from sqlalchemy.types import DateTime, Float, Numeric

from ...unrest import UnRest
from .. import idsorted
from ..model import Fruit, Tree

results = [
    {
        'fruit_id': 1,
        'color': 'grey',
        'size': 12.0,
        'double_size': 24.0,
        'age': 1_041_300.0,
        'tree_id': 1,
        'square_size': 144.0,
    },
    {
        'fruit_id': 2,
        'color': 'darkgrey',
        'size': 23.0,
        'double_size': 46.0,
        'age': 4_233_830.213,
        'tree_id': 1,
        'square_size': 529.0,
    },
    {
        'fruit_id': 3,
        'color': 'brown',
        'size': 2.12,
        'double_size': 4.24,
        'age': 0.0,
        'tree_id': 1,
        'square_size': 4.4944,
    },
    {
        'fruit_id': 4,
        'color': 'red',
        'size': 0.5,
        'double_size': 1.0,
        'age': 2400.0,
        'tree_id': 2,
        'square_size': 0.25,
    },
    {
        'fruit_id': 5,
        'color': 'orangered',
        'size': 100.0,
        'double_size': 200.0,
        'age': 7200.000_012,
        'tree_id': None,
        'square_size': 10000.0,
    },
]


def test_get_tree_with_property(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, properties=['fruit_colors'])
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine', 'fruit_colors': 'grey, darkgrey, brown'},
        {'id': 2, 'name': 'maple', 'fruit_colors': 'red'},
        {'id': 3, 'name': 'oak', 'fruit_colors': None},
    ]


def test_get_tree_with_object_property(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, properties=[rest.Property('fruit_colors')])
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine', 'fruit_colors': 'grey, darkgrey, brown'},
        {'id': 2, 'name': 'maple', 'fruit_colors': 'red'},
        {'id': 3, 'name': 'oak', 'fruit_colors': None},
    ]


def test_get_fruit_with_hybrid_property_and_type(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, properties=[rest.Property('square_size', Float())])
    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == results


def test_get_fruit_with_hybrid_property_and_formatter(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(
        Fruit,
        properties=[
            rest.Property('square_size', formatter=lambda x: float(x))
        ],
    )
    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == results


def test_get_fruit_with_primary_keys(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, primary_keys=['fruit_id', 'age'], only=[])
    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert json['primary_keys'] == ['fruit_id', 'age']
    assert idsorted(json['objects'], 'fruit_id') == [
        {'fruit_id': 1, 'age': 1_041_300.0},
        {'fruit_id': 2, 'age': 4_233_830.213},
        {'fruit_id': 3, 'age': 0.0},
        {'fruit_id': 4, 'age': 2400.0},
        {'fruit_id': 5, 'age': 7200.000_012},
    ]


def test_get_tree_with_hybrid_property_as_primary_key(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(
        Fruit,
        primary_keys=['square_size'],
        only=[],
        properties=[rest.Property('square_size', type=Numeric())],
    )
    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert json['primary_keys'] == ['square_size']
    assert idsorted(json['objects'], 'square_size') == [
        {'square_size': 0.25},
        {'square_size': 4.4944},
        {'square_size': 144.0},
        {'square_size': 529.0},
        {'square_size': 10000.0},
    ]


def test_get_tree_pk_with_hybrid_property_as_primary_key(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(
        Fruit,
        primary_keys=['square_size'],
        only=[],
        properties=[rest.Property('square_size', type=Numeric())],
    )
    code, json = client.fetch('/api/fruit/0.25')
    assert code == 200
    assert json['occurences'] == 1
    assert json['primary_keys'] == ['square_size']
    assert idsorted(json['objects'], 'square_size') == [{'square_size': 0.25}]


def test_datetime_properties(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(
        Fruit, only=[], properties=[rest.Property('birthday', type=DateTime())]
    )
    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == [
        {'fruit_id': 1, 'birthday': '2019-12-19T22:45:00'},
        {'fruit_id': 2, 'birthday': '2019-11-12T23:56:09.787000'},
        {'fruit_id': 3, 'birthday': '2020-01-01T00:00:00'},
        {'fruit_id': 4, 'birthday': '2019-12-31T23:20:00'},
        {'fruit_id': 5, 'birthday': '2019-12-31T21:59:59.999988'},
    ]
