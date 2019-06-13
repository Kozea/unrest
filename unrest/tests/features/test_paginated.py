from ...idiom.unrest import UnRestIdiom
from ...unrest import UnRest
from .. import idsorted
from ..model import Tree


def test_paginated(client):
    class PaginatedUnRestIdiom(UnRestIdiom):
        def alter_query(client, request, query):
            offset = int(request.query.get('offset', [0])[0])
            step = int(request.query.get('step', [2])[0])
            return query.offset(offset).limit(step)

    rest = UnRest(
        client.app,
        client.session,
        framework=client.__framework__,
        idiom=PaginatedUnRestIdiom,
    )
    rest(Tree)
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert json['limit'] == 2
    assert json['offset'] == 0
    assert json['primary_keys'] == ['id']
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
    ]
    code, json = client.fetch('/api/tree?offset=1')
    assert code == 200
    assert json['occurences'] == 3
    assert json['limit'] == 2
    assert json['offset'] == 1
    assert json['primary_keys'] == ['id']
    assert idsorted(json['objects']) == [
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]
    code, json = client.fetch('/api/tree?offset=2')
    assert code == 200
    assert json['occurences'] == 3
    assert json['limit'] == 2
    assert json['offset'] == 2
    assert json['primary_keys'] == ['id']
    assert idsorted(json['objects']) == [{'id': 3, 'name': 'oak'}]
    code, json = client.fetch('/api/tree?offset=3')
    assert code == 200
    assert json['occurences'] == 3
    assert json['limit'] == 2
    assert json['offset'] == 3
    assert json['primary_keys'] == ['id']
    assert idsorted(json['objects']) == []
