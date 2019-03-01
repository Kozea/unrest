import sys

from pytest import raises

from unrest import UnRest

from .. import idsorted
from ...idiom import Idiom
from ...idiom.unrest import UnRestIdiom
from ...idiom.yaml import YamlIdiom
from ...util import Response
from ..model import Tree


def test_idiom(client):
    class FakeIdiom(Idiom):
        def request_to_payload(client, request):
            if request.method == 'PUT':
                return {'name': 'sth'}

        def data_to_response(client, data, method, status=200):
            payload = 'Hello %d' % data['occurences']
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
            if request.method == 'PUT':
                return {'name': 'sth'}


    rest = UnRest(
        client.app,
        client.session,
        idiom=FakeIdiom,
        framework=client.__framework__,
    )
    rest(Tree, methods=['GET', 'PUT'])
    code, html = client.fetch('/api/tree')
    assert code == 500

def test_idiom_partial_implementation_bis(client):
    class FakeIdiom(Idiom):
        def data_to_response(client, data, method, status=200):
            payload = 'Hello %d' % data['occurences']
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
