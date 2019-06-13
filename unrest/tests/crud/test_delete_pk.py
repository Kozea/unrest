from ...unrest import UnRest
from .. import idsorted
from ..model import Fruit, Tree


def test_delete_tree(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'DELETE'])
    code, json = client.fetch('/api/tree/2', method="DELETE")
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [{'id': 2, 'name': 'maple'}]

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 2
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 3, 'name': 'oak'},
    ]


def test_delete_unknown_tree(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['DELETE'])
    code, json = client.fetch('/api/tree/9', method="DELETE")
    assert code == 404


def test_delete_fruit(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Fruit, methods=['GET', 'DELETE'])
    code, json = client.fetch('/api/fruit/2', method="DELETE")
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects'], 'fruit_id') == [
        {
            'fruit_id': 2,
            'color': 'darkgrey',
            'size': 23.0,
            'double_size': 46.0,
            'age': 4_233_830.213,
            'tree_id': 1,
        }
    ]

    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 4
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
