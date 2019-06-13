from ...unrest import UnRest
from .. import idsorted
from ..model import Fruit, Tree


def test_get_tree_with_relationship(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    fruit = rest(Fruit, methods=[], only=['color'])

    rest(Tree, relationships={'fruits': fruit})
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {
            'id': 1,
            'name': 'pine',
            'fruits': [
                {'fruit_id': 1, 'color': 'grey'},
                {'fruit_id': 2, 'color': 'darkgrey'},
                {'fruit_id': 3, 'color': 'brown'},
            ],
        },
        {
            'id': 2,
            'name': 'maple',
            'fruits': [{'fruit_id': 4, 'color': 'red'}],
        },
        {'id': 3, 'name': 'oak', 'fruits': []},
    ]
    code, json = client.fetch('/api/fruit')
    assert code == 404


def test_get_fruit_with_relationship(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    tree = rest(Tree, methods=[])
    rest(Fruit, only=['color'], relationships={'tree': tree})

    code, json = client.fetch('/api/fruit')
    assert code == 200
    assert json['occurences'] == 5
    assert idsorted(json['objects'], 'fruit_id') == [
        {'fruit_id': 1, 'color': 'grey', 'tree': [{'id': 1, 'name': 'pine'}]},
        {
            'fruit_id': 2,
            'color': 'darkgrey',
            'tree': [{'id': 1, 'name': 'pine'}],
        },
        {'fruit_id': 3, 'color': 'brown', 'tree': [{'id': 1, 'name': 'pine'}]},
        {'fruit_id': 4, 'color': 'red', 'tree': [{'id': 2, 'name': 'maple'}]},
        {'fruit_id': 5, 'color': 'orangered', 'tree': []},
    ]
    code, json = client.fetch('/api/tree')
    assert code == 404


def test_virtual(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)

    rest(Tree, relationships={'fruits': rest.virtual(Fruit, only=['color'])})
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {
            'id': 1,
            'name': 'pine',
            'fruits': [
                {'fruit_id': 1, 'color': 'grey'},
                {'fruit_id': 2, 'color': 'darkgrey'},
                {'fruit_id': 3, 'color': 'brown'},
            ],
        },
        {
            'id': 2,
            'name': 'maple',
            'fruits': [{'fruit_id': 4, 'color': 'red'}],
        },
        {'id': 3, 'name': 'oak', 'fruits': []},
    ]
    code, json = client.fetch('/api/fruit')
    assert code == 404


def test_virtual_enforce_no_methods_args(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)

    rest(Tree, relationships={'fruits': rest.virtual(Fruit, rest.all)})
    code, json = client.fetch('/api/fruit')
    assert code == 404


def test_virtual_enforce_no_methods_kwargs(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)

    rest(Tree, relationships={'fruits': rest.virtual(Fruit, methods=rest.all)})
    code, json = client.fetch('/api/fruit')
    assert code == 404
