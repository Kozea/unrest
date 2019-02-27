from unrest import UnRest

from .. import idsorted
from ...idiom import Idiom
from ...idiom.unrest import UnRestIdiom
from ...idiom.yaml import YamlIdiom
from ...util import Response
from ..model import Tree


class IdiomTestCollection(object):
    def test_idiom(self):
        class FakeIdiom(Idiom):
            def request_to_payload(self, request):
                if request.method == 'PUT':
                    return {'name': 'sth'}

            def data_to_response(self, data, method, status=200):
                payload = 'Hello %d' % data['occurences']
                headers = {'Content-Type': 'text/plain'}
                response = Response(payload, headers, status)
                return response

        rest = UnRest(
            self.app,
            self.session,
            idiom=FakeIdiom,
            framework=self.__framework__,
        )
        rest(Tree, methods=['GET', 'PUT'])
        code, html = self.fetch('/api/tree')
        assert code == 200
        assert html == 'Hello 3'

        code, html = self.fetch(
            '/api/tree/1', method="PUT", json={'id': 1, 'name': 'cedar'}
        )
        assert code == 200
        assert html == 'Hello 1'

        code, html = self.fetch('/api/tree')
        assert code == 200
        assert html == 'Hello 3'

    def test_idiom_alter_query(self):
        class FakeIdiom(UnRestIdiom):
            def alter_query(self, request, query):
                if request.query.get('limit'):
                    query = query.limit(request.query['limit'][0])
                return query

        rest = UnRest(
            self.app,
            self.session,
            idiom=FakeIdiom,
            framework=self.__framework__,
        )
        tree = rest(Tree, methods=['GET', 'PUT'])
        assert tree.query.count() == 3

        code, json = self.fetch('/api/tree?limit=1')
        assert code == 200
        assert idsorted(json['objects']) == [{'id': 1, 'name': 'pine'}]

        code, json = self.fetch('/api/tree?limit=2')
        assert code == 200
        assert idsorted(json['objects']) == [
            {'id': 1, 'name': 'pine'},
            {'id': 2, 'name': 'maple'},
        ]

        code, json = self.fetch('/api/tree')
        assert code == 200
        assert idsorted(json['objects']) == [
            {'id': 1, 'name': 'pine'},
            {'id': 2, 'name': 'maple'},
            {'id': 3, 'name': 'oak'},
        ]

        assert tree.query.count() == 3

    def test_yaml_idiom_get(self):
        rest = UnRest(
            self.app,
            self.session,
            idiom=YamlIdiom,
            framework=self.__framework__,
        )
        rest(Tree)

        code, yaml = self.fetch('/api/tree')
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

    def test_yaml_idiom_put(self):
        rest = UnRest(
            self.app,
            self.session,
            idiom=YamlIdiom,
            framework=self.__framework__,
        )
        rest(Tree, methods=['GET', 'PUT'], allow_batch=True)

        code, yaml = self.fetch(
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

        code, yaml = self.fetch('/api/tree')
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
