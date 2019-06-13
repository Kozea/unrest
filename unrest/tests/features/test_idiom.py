import sys

from pytest import raises

from unrest import UnRest

from ...idiom import Idiom
from ...idiom.json_server import JsonServerIdiom
from ...idiom.unrest import UnRestIdiom
from ...idiom.yaml import YamlIdiom
from ...util import Response
from .. import idsorted
from ..model import Fruit, Tree


def test_idiom(client):
    class FakeIdiom(Idiom):
        def request_to_payload(client, request):
            if request.method == 'PUT':
                return {'name': 'sth'}

        def data_to_response(client, data, method, status=200):
            payload = f"Hello {data['occurences']}"
            headers = {'Content-Type': 'text/plain'}
            response = Response(payload, headers, status)
            return response

    rest = UnRest(
        client.app,
        client.session,
        idiom=FakeIdiom,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'PUT'])
    code, html = client.fetch('/api/tree')
    assert code == 200
    assert html == 'Hello 3'

    code, html = client.fetch(
        '/api/tree/1', method="PUT", json={'id': 1, 'name': 'cedar'}
    )
    assert code == 200
    assert html == 'Hello 1'

    code, html = client.fetch('/api/tree')
    assert code == 200
    assert html == 'Hello 3'


def test_idiom_alter_query(client):
    class FakeIdiom(UnRestIdiom):
        def alter_query(client, request, query):
            if request.query.get('limit'):
                query = query.limit(request.query['limit'][0])
            return query

    rest = UnRest(
        client.app,
        client.session,
        idiom=FakeIdiom,
        framework=client.__framework__,
    )
    tree = rest(Tree, methods=['GET', 'PUT'])
    assert tree.query.count() == 3

    code, json = client.fetch('/api/tree?limit=1')
    assert code == 200
    assert idsorted(json['objects']) == [{'id': 1, 'name': 'pine'}]

    code, json = client.fetch('/api/tree?limit=2')
    assert code == 200
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
    ]

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert idsorted(json['objects']) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]

    assert tree.query.count() == 3


def test_idiom_partial_implementation(client):
    class FakeIdiom(Idiom):
        def request_to_payload(client, request):
            pass

    rest = UnRest(
        client.app,
        client.session,
        idiom=FakeIdiom,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'PUT'])
    code, html = client.fetch('/api/tree')
    assert code == 500


def test_idiom_no_implementation(client):
    rest = UnRest(
        client.app, client.session, idiom=Idiom, framework=client.__framework__
    )
    rest(Tree, methods=['GET', 'PUT'])
    code, html = client.fetch('/api/tree')
    assert code == 500


def test_yaml_idiom_get(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=YamlIdiom,
        framework=client.__framework__,
    )
    rest(Tree)

    code, yaml = client.fetch('/api/tree')
    assert code == 200
    assert (
        yaml
        == '''\
objects:
- id: 1
  name: pine
- id: 2
  name: maple
- id: 3
  name: oak
occurences: 3
primary_keys:
- id
'''
    )


def test_yaml_idiom_put(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=YamlIdiom,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'PUT'], allow_batch=True)

    code, yaml = client.fetch(
        '/api/tree',
        method="PUT",
        body='''\
objects:
- id: 1
  name: cedar
- id: 2
  name: mango
''',
    )
    assert (
        yaml
        == '''\
objects:
- id: 1
  name: cedar
- id: 2
  name: mango
occurences: 2
primary_keys:
- id
'''
    )

    code, yaml = client.fetch('/api/tree')
    assert code == 200
    assert (
        yaml
        == '''\
objects:
- id: 1
  name: cedar
- id: 2
  name: mango
occurences: 2
primary_keys:
- id
'''
    )


def test_yaml_idiom_put_bad_formed(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=YamlIdiom,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'PUT'], allow_batch=True)

    code, yaml = client.fetch(
        '/api/tree',
        method="PUT",
        body='''\
objects: ][
''',
    )
    assert code == 400
    assert (
        yaml
        == '''message: "YAML Error in payload: while parsing a block node\
\\nexpected the node content,\\\n  \\ but found \']\'\\n  in \
\\"<unicode string>\\", line 1, column 10:\\n    objects: ][\\n\\\n  \
\\             ^"
'''
    )


def test_yaml_idiom_no_yaml(client):
    sys.modules['yaml'] = None
    rest = UnRest(
        client.app,
        client.session,
        idiom=YamlIdiom,
        framework=client.__framework__,
    )

    with raises(ImportError):
        rest(Tree, methods=['GET', 'PUT'], allow_batch=True)

    del sys.modules['yaml']


def test_yaml_idiom_empty_get_pk_as_404(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=YamlIdiom,
        framework=client.__framework__,
        empty_get_as_404=True,
    )
    rest(Tree)
    code, yaml = client.fetch('/api/tree/6')
    assert code == 404
    assert (
        yaml
        == '''\
objects: []
occurences: 0
primary_keys:
- id
'''
    )


def test_json_server_get_tree(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Tree)
    rest(Fruit)
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert idsorted(json) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]


def test_json_server_post_tree(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'POST'])
    code, json = client.fetch(
        '/api/tree', method="POST", json={'name': 'cedar'}
    )
    assert code == 200
    assert json == {'id': 4, 'name': 'cedar'}

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert idsorted(json) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
        {'id': 4, 'name': 'cedar'},
    ]


def test_json_server_put_tree(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'PUT'])
    code, json = client.fetch(
        '/api/tree/1', method="PUT", json={'name': 'cedar'}
    )
    assert code == 200
    assert json == {'id': 1, 'name': 'cedar'}

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert idsorted(json) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]


def test_json_server_put_trees(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'PUT'], allow_batch=True)
    code, json = client.fetch(
        '/api/tree',
        method="PUT",
        json=[{'id': 1, 'name': 'cedar'}, {'id': 2, 'name': 'mango'}],
    )
    assert code == 200
    assert idsorted(json) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'mango'},
    ]

    code, json = client.fetch('/api/tree')
    assert code == 200
    assert idsorted(json) == [
        {'id': 1, 'name': 'cedar'},
        {'id': 2, 'name': 'mango'},
    ]


def test_json_server_delete_trees(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        empty_get_as_404=True,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'DELETE'], allow_batch=True)
    code, json = client.fetch('/api/tree', method="DELETE")
    assert code == 200
    assert idsorted(json) == [
        {'id': 1, 'name': 'pine'},
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
    ]

    code, json = client.fetch('/api/tree')
    assert code == 404


def test_json_server_get_tree_with_relationship(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    fruit = rest(Fruit, methods=[], only=['color'])

    rest(Tree, relationships={'fruits': fruit})
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert idsorted(json) == [
        {'id': 1, 'name': 'pine', 'fruits': [1, 2, 3]},
        {'id': 2, 'name': 'maple', 'fruits': [4]},
        {'id': 3, 'name': 'oak', 'fruits': []},
    ]
    code, json = client.fetch('/api/fruit')
    assert code == 404


def test_json_server_get_tree_with_relationship_with_multi_pk(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    fruit = rest(Fruit, methods=[], primary_keys=['color', 'age'])

    rest(Tree, relationships={'fruits': fruit})
    code, json = client.fetch('/api/tree')
    assert code == 200
    assert idsorted(json) == [
        {
            'id': 1,
            'name': 'pine',
            'fruits': [
                'grey___1041300.0',
                'darkgrey___4233830.213',
                'brown___0.0',
            ],
        },
        {'id': 2, 'name': 'maple', 'fruits': ['red___2400.0']},
        {'id': 3, 'name': 'oak', 'fruits': []},
    ]
    code, json = client.fetch('/api/fruit')
    assert code == 404


def test_json_server_bad_json(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'POST'])
    code, json = client.fetch(
        '/api/tree', method="POST", body="{'name'; 'cedar'}"
    )
    assert code == 400
    assert (
        json['message'] == 'JSON Error in payload: '
        'Expecting property name enclosed in double quotes: '
        'line 1 column 2 (char 1)'
    )


def test_json_server_filter_fruits(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Fruit)
    code, json = client.fetch('/api/fruit?color=red')
    assert code == 200
    assert idsorted(json, 'fruit_id') == [
        {
            'fruit_id': 4,
            'color': 'red',
            'size': 0.5,
            'double_size': 1.0,
            'age': 2400.0,
            'tree_id': 2,
        }
    ]
    code, json = client.fetch('/api/fruit?color=red&color=brown')
    assert code == 200
    assert idsorted(json, 'fruit_id') == [
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
    ]


def test_json_server_filter_fruits_gte(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Fruit)
    code, json = client.fetch('/api/fruit?color_gte=forestgreen')
    assert code == 200
    assert idsorted(json, 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'grey',
            'size': 12.0,
            'double_size': 24.0,
            'age': 1_041_300.0,
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


def test_json_server_filter_fruits_lte(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Fruit)
    code, json = client.fetch('/api/fruit?size_lte=4')
    assert code == 200
    assert idsorted(json, 'fruit_id') == [
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
    ]


def test_json_server_filter_fruits_ne(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Fruit)
    code, json = client.fetch('/api/fruit?age_ne=1970-01-01%2000:40:00.000000')
    assert code == 200
    assert idsorted(json, 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'grey',
            'size': 12.0,
            'double_size': 24.0,
            'age': 1_041_300.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 2,
            'color': 'darkgrey',
            'size': 23.0,
            'double_size': 46.0,
            'age': 4_233_830.213,
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
            'fruit_id': 5,
            'color': 'orangered',
            'size': 100.0,
            'double_size': 200.0,
            'age': 7200.000_012,
            'tree_id': None,
        },
    ]


def test_json_server_filter_fruits_like(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Fruit)
    code, json = client.fetch('/api/fruit?color_like=gre')
    assert code == 200
    assert idsorted(json, 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'grey',
            'size': 12.0,
            'double_size': 24.0,
            'age': 1_041_300.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 2,
            'color': 'darkgrey',
            'size': 23.0,
            'double_size': 46.0,
            'age': 4_233_830.213,
            'tree_id': 1,
        },
    ]


def test_json_server_filter_fruits_q(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Fruit)
    code, json = client.fetch('/api/fruit?q=gre')
    assert code == 200
    assert idsorted(json, 'fruit_id') == [
        {
            'fruit_id': 1,
            'color': 'grey',
            'size': 12.0,
            'double_size': 24.0,
            'age': 1_041_300.0,
            'tree_id': 1,
        },
        {
            'fruit_id': 2,
            'color': 'darkgrey',
            'size': 23.0,
            'double_size': 46.0,
            'age': 4_233_830.213,
            'tree_id': 1,
        },
    ]


def test_json_server_sort(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Tree)
    code, json = client.fetch('/api/tree?_sort=name')
    assert code == 200
    assert json == [
        {'id': 2, 'name': 'maple'},
        {'id': 3, 'name': 'oak'},
        {'id': 1, 'name': 'pine'},
    ]


def test_json_server_sort_desc(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Tree)
    code, json = client.fetch('/api/tree?_sort=name&_order=desc')
    assert code == 200
    assert json == [
        {'id': 1, 'name': 'pine'},
        {'id': 3, 'name': 'oak'},
        {'id': 2, 'name': 'maple'},
    ]


def test_json_server_sort_multiple(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'POST'])
    client.fetch('/api/tree', method="POST", json={'name': 'pine'})
    client.fetch('/api/tree', method="POST", json={'name': 'oak'})
    client.fetch('/api/tree', method="POST", json={'name': 'oak'})

    code, json = client.fetch('/api/tree?_sort=name,id&_order=asc,desc')
    assert code == 200
    assert json == [
        {'id': 2, 'name': 'maple'},
        {'id': 6, 'name': 'oak'},
        {'id': 5, 'name': 'oak'},
        {'id': 3, 'name': 'oak'},
        {'id': 4, 'name': 'pine'},
        {'id': 1, 'name': 'pine'},
    ]


def test_json_server_sort_rel_hack(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Tree, query=lambda q: q.join(Fruit))
    code, json = client.fetch('/api/tree?_sort=fruit.size')
    assert code == 200
    assert json == [{'id': 2, 'name': 'maple'}, {'id': 1, 'name': 'pine'}]


def test_json_server_slice(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Fruit, only=['color'])
    code, json = client.fetch('/api/fruit?_start=1&_end=3')
    assert code == 200
    assert json == [
        {'fruit_id': 2, 'color': 'darkgrey'},
        {'fruit_id': 3, 'color': 'brown'},
    ]


def test_json_server_paginate(client):
    rest = UnRest(
        client.app,
        client.session,
        idiom=JsonServerIdiom,
        framework=client.__framework__,
    )
    rest(Fruit, only=['color'])
    code, json = client.fetch('/api/fruit?_page=2&_limit=2')
    assert code == 200
    print(json)
    assert json == [
        {'fruit_id': 3, 'color': 'brown'},
        {'fruit_id': 4, 'color': 'red'},
    ]
