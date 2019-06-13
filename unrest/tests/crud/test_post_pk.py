from ...unrest import UnRest
from .. import idsorted
from ..model import Tree


def test_post_tree_with_pk(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    rest(Tree, methods=['GET', 'POST'])
    code, json = client.fetch(
        '/api/tree/6', method="POST", json={'name': 'mango'}
    )
    assert code == 501


def test_post_tree_with_pk_custom(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)
    tree = rest(Tree)

    @tree.declare('POST')
    def post(payload, id=None):
        # Make it work anyway
        return tree.post(payload)

    code, json = client.fetch(
        '/api/tree/9', method="POST", json={'name': 'mango'}
    )
    assert code == 200
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [{'id': 4, 'name': 'mango'}]

    code, json = client.fetch('/api/tree')
    assert json['occurences'] == 4
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
        {'id': 4, 'name': 'mango'},
    ]
