from . import idsorted
from ..model import Tree


def test_paginated(rest, http):
    def paginated(query_factory, step=2):
        from flask import request

        def limited_query(query):
            if query_factory is not None:
                query = query_factory(query)
            offset = int(request.values.get('offset', 0))
            return query.offset(offset).limit(step)
        return limited_query

    rest(Tree, query=paginated(lambda query: query))
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert json['limit'] == 2
    assert json['offset'] == 0
    assert json['primary_keys'] == ['id']
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
    ]
    code, json = http.get('/api/tree?offset=1')
    assert code == 200
    assert json['occurences'] == 3
    assert json['limit'] == 2
    assert json['offset'] == 1
    assert json['primary_keys'] == ['id']
    assert idsorted(json['objects']) == [
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]
    code, json = http.get('/api/tree?offset=2')
    assert code == 200
    assert json['occurences'] == 3
    assert json['limit'] == 2
    assert json['offset'] == 2
    assert json['primary_keys'] == ['id']
    assert idsorted(json['objects']) == [
        {'id': 3, 'name': 'oak'},
    ]
    code, json = http.get('/api/tree?offset=3')
    assert code == 200
    assert json['occurences'] == 3
    assert json['limit'] == 2
    assert json['offset'] == 3
    assert json['primary_keys'] == ['id']
    assert idsorted(json['objects']) == []
