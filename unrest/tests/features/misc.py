import sys

from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.types import Boolean, Float, String

from unrest import UnRest, __about__
from unrest.coercers import Deserialize, Serialize
from unrest.rest import Rest

from .. import idsorted
from ...framework import Framework
from ...framework.flask import FlaskFramework
from ..model import Fruit, Tree
from ..static.openapi_result import openapi


class MiscellaneousTestCollection(object):
    def test_other_url(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree)
        code, html = self.fetch('/')
        assert code == 200
        assert html == 'A normal route!'

    def test_index(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree)
        code, html = self.fetch('/api/')
        assert code == 200
        assert (
            html
            == (
                '<h1>unrest <small>api server</small></h1> version %s '
                '<a href="https://github.com/Kozea/unrest">unrest</a> '
                '<a href="/api/openapi.json">openapi.json</a>'
            )
            % __about__.__version__
        )

    def test_normal(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree)
        code, json = self.fetch('/api/tree')
        assert code == 200
        assert json['occurences'] == 3

    def test_path(self):
        rest = UnRest(
            self.app, self.session, '/forest', framework=self.__framework__
        )
        rest(Tree)
        code, json = self.fetch('/forest/tree')
        assert code == 200
        assert json['occurences'] == 3

    def test_schema(self):
        Tree.__table__.schema = 'forest'

        def reset_schema(query):
            Tree.__table__.schema = None
            return query

        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, query=reset_schema)
        code, json = self.fetch('/api/forest/tree')
        assert code == 200
        assert json['occurences'] == 3

    def test_version(self):
        rest = UnRest(
            self.app,
            self.session,
            version='v3.14',
            framework=self.__framework__,
        )
        rest(Tree)
        code, json = self.fetch('/api/v3.14/tree')
        assert code == 200
        assert json['occurences'] == 3

    def test_path_and_version(self):
        rest = UnRest(
            self.app,
            self.session,
            '/forest',
            'v3.14',
            framework=self.__framework__,
        )
        rest(Tree)
        code, json = self.fetch('/forest/v3.14/tree')
        assert code == 200
        assert json['occurences'] == 3

    def test_normal_rest_class(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        tree = rest(Tree, name='tree')
        assert isinstance(tree, Rest)

    def test_alternative_rest_class(self):
        class NewRest(Rest):
            def __init__(self, *args, **kwargs):
                kwargs['name'] = 'new_' + kwargs['name']
                super().__init__(*args, **kwargs)

        new_rest = UnRest(
            self.app,
            self.session,
            framework=self.__framework__,
            RestClass=NewRest,
        )
        new_tree = new_rest(Tree, name='tree')
        assert isinstance(new_tree, NewRest)

        code, json = self.fetch('/api/tree')
        assert code == 404
        code, json = self.fetch('/api/new_tree')
        assert code == 200
        assert json['occurences'] == 3

    def test_empty_get_pk_as_404(self):
        rest = UnRest(
            self.app,
            self.session,
            framework=self.__framework__,
            empty_get_as_404=True,
        )
        rest(Tree)
        code, json = self.fetch('/api/tree/6')
        assert code == 404
        assert json['occurences'] == 0
        assert json['objects'] == []

    def test_empty_explicit_framework(self):
        class FakeUnRest(object):
            def __init__(self, app, url):
                pass

            def register_route(self, *args, **kwargs):
                pass

        rest = UnRest(self.app, self.session, framework=FakeUnRest)
        rest(Tree)
        code, _ = self.fetch('/api/tree')
        assert code == 404

    def test_api_options(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        fruit = rest(Fruit)
        rest(
            Tree,
            methods=rest.all,
            relationships={'fruits': fruit},
            properties=['fruit_colors'],
            allow_batch=True,
        )
        code, json = self.fetch('/api', method="OPTIONS")
        assert code == 200
        assert json == {
            '/api/fruit': {
                'model': 'Fruit',
                'description': 'A bag of fruit',
                'parameters': ['fruit_id'],
                'columns': {
                    'age': 'timedelta',
                    'color': 'str',
                    'fruit_id': 'int',
                    'size': 'Decimal',
                    'tree_id': 'int',
                    'double_size': 'Decimal',
                },
                'properties': {},
                'relationships': {},
                'methods': ['GET', 'OPTIONS'],
                'batch': False,
            },
            '/api/tree': {
                'model': 'Tree',
                'description': "Where money doesn't grow",
                'parameters': ['id'],
                'columns': {'id': 'int', 'name': 'str'},
                'properties': {'fruit_colors': 'str'},
                'relationships': {
                    'fruits': {
                        'model': 'Fruit',
                        'description': 'A bag of fruit',
                        'parameters': ['fruit_id'],
                        'columns': {
                            'age': 'timedelta',
                            'color': 'str',
                            'fruit_id': 'int',
                            'size': 'Decimal',
                            'tree_id': 'int',
                            'double_size': 'Decimal',
                        },
                        'properties': {},
                        'relationships': {},
                        'batch': False,
                    }
                },
                'methods': [
                    'GET',
                    'PUT',
                    'POST',
                    'DELETE',
                    'PATCH',
                    'OPTIONS',
                ],
                'batch': True,
            },
        }

    def test_endpoint_options(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        fruit = rest(Fruit)
        rest(
            Tree,
            methods=rest.all,
            relationships={'fruits': fruit},
            properties=['fruit_colors'],
            allow_batch=True,
        )
        code, json = self.fetch('/api/fruit', method="OPTIONS")
        assert code == 200
        assert json == {
            'model': 'Fruit',
            'description': 'A bag of fruit',
            'batch': False,
            'parameters': ['fruit_id'],
            'columns': {
                'age': 'timedelta',
                'color': 'str',
                'fruit_id': 'int',
                'size': 'Decimal',
                'tree_id': 'int',
                'double_size': 'Decimal',
            },
            'properties': {},
            'relationships': {},
            'methods': ['GET', 'OPTIONS'],
        }

    def test_endpoint_options_no_methods(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, methods=[])
        code, json = self.fetch('/api/tree', method="OPTIONS")
        assert code == 404

    def test_endpoint_options_no_methods_but_declare(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        tree = rest(Tree, methods=[])

        @tree.declare('GET')
        def get(payload, id=None):
            return {'Hey': 'Overridden'}

        @tree.declare('POST')
        def post(payload, id=None):
            return {'Hey': 'Overridden'}

        code, json = self.fetch('/api/tree', method="OPTIONS")
        assert code == 200

    def test_openapi(self):
        rest = UnRest(
            self.app,
            self.session,
            info={
                'description': '''# Unrest demo
This is the demo of unrest api.
This api expose the `Tree` and `Fruit` entity Rest methods.
''',
                'contact': {
                    'name': __about__.__author__,
                    'url': __about__.__uri__,
                    'email': __about__.__email__,
                },
                'license': {'name': __about__.__license__},
            },
            framework=self.__framework__,
        )
        fruit = rest(
            Fruit,
            methods=rest.all,
            properties=[rest.Property('square_size', Float())],
        )
        rest(
            Tree,
            methods=rest.all,
            relationships={'fruits': fruit},
            properties=['fruit_colors'],
            allow_batch=True,
        )
        code, json = self.fetch('/api/openapi.json')
        # Only flask supports absolute url
        if 'Flask' not in self.__framework__.__name__:
            res = {**openapi, 'servers': [{'url': '/api'}]}
        else:
            res = openapi
        assert code == 200
        assert json == res

    def test_openapi_other_type(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(
            Tree,
            properties=[
                rest.Property('fake_prop_1', type=Boolean()),
                rest.Property('fake_prop_2', type=INET()),
            ],
        )
        code, json = self.fetch('/api/openapi.json')
        assert code == 200
        assert json['paths']['/tree']['get']['responses']['200']['content'][
            'application/json'
        ]['schema']['properties']['objects']['items']['properties'] == {
            'fake_prop_1': {'type': 'boolean'},
            'fake_prop_2': {'type': 'string'},
            'id': {'format': 'int64', 'type': 'integer'},
            'name': {'type': 'string'},
        }

    def test_sub(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)

        fruit = rest(
            Fruit,
            methods=rest.all,
            properties=[rest.Property('square_size', Float())],
        )
        tree = rest(
            Tree,
            methods=rest.all,
            relationships={'fruits': fruit},
            properties=['fruit_colors'],
            query=lambda q: q.filter(Tree.name != 'pine'),
            allow_batch=True,
        )
        subtree = tree.sub(lambda q: q.filter(Tree.name != 'oak'))
        for key in [
            'unrest',
            'Model',
            'methods',
            'only',
            'exclude',
            'properties',
            'relationships',
            'allow_batch',
            'auth',
            'read_auth',
            'write_auth',
            'validators',
            '_primary_keys',
            'SerializeClass',
            'DeserializeClass',
        ]:
            assert getattr(subtree, key) == getattr(tree, key)
        assert subtree.name == 'subtree'

        code, json = self.fetch('/api/tree')
        assert code == 200
        assert json['occurences'] == 2

        code, json = self.fetch('/api/subtree')
        assert code == 200
        assert json['occurences'] == 1

        subtree = tree.sub(
            lambda q: q.filter(Tree.name != 'maple'), name='nomaple'
        )
        code, json = self.fetch('/api/nomaple')
        assert code == 200
        assert json['occurences'] == 1

    def test_sub_fixed(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)

        fruit = rest(
            Fruit,
            defaults={'size': 1.0},
            fixed={'color': 'blue'},
            methods=rest.all,
            properties=[rest.Property('square_size', Float())],
        )
        subfruit = fruit.sub(lambda q: q.filter(Fruit.age == 2.0))
        for key in ['defaults', 'fixed']:
            assert getattr(subfruit, key) == getattr(fruit, key)

    def test_wrong_framework(self):
        try:
            UnRest(self.app, self.session, framework=Framework)
        except NotImplementedError:
            pass
        else:
            raise Exception('Should have raised')  # pragma: no cover

    def test_auto_framework(self):
        if 'Flask' not in self.__framework__.__name__:
            return
        rest = UnRest(self.app, self.session)
        assert isinstance(rest.framework, FlaskFramework)

    def test_no_framework(self):
        if 'Flask' not in self.__framework__.__name__:
            return
        flask = sys.modules['flask']
        sys.modules['flask'] = None
        try:
            UnRest(self.app, self.session)
        except NotImplementedError:
            pass
        else:
            raise Exception('Should have raised')  # pragma: no cover
        sys.modules['flask'] = flask

    def test_custom_serialization(self):
        class UpperCaseStringSerialize(Serialize):
            def serialize(self, name, column):
                rv = super().serialize(name, column)
                if isinstance(column.type, String):
                    return rv.upper()
                return rv

        rest = UnRest(
            self.app,
            self.session,
            SerializeClass=UpperCaseStringSerialize,
            framework=self.__framework__,
        )
        rest(Tree, methods=['GET', 'PUT'])

        code, json = self.fetch('/api/tree')
        assert code == 200
        assert json['occurences'] == 3
        assert idsorted(json['objects']) == [
            {'id': 1, 'name': 'PINE'},
            {'id': 2, 'name': 'MAPLE'},
            {'id': 3, 'name': 'OAK'},
        ]

    def test_custom_deserialization(self):
        class UpperCaseStringDeserialize(Deserialize):
            def deserialize(self, name, column, payload=None):
                rv = super().deserialize(name, column, payload)
                if isinstance(column.type, String):
                    return rv.upper()
                return rv

        rest = UnRest(
            self.app,
            self.session,
            DeserializeClass=UpperCaseStringDeserialize,
            framework=self.__framework__,
        )
        rest(Tree, methods=['GET', 'PUT'])

        code, json = self.fetch(
            '/api/tree/1', method="PUT", json={'id': 1, 'name': 'cedar'}
        )
        assert code == 200
        assert json['occurences'] == 1
        assert idsorted(json['objects']) == [{'id': 1, 'name': 'CEDAR'}]

        code, json = self.fetch('/api/tree')
        assert code == 200
        assert json['occurences'] == 3
        assert idsorted(json['objects']) == [
            {'id': 1, 'name': 'CEDAR'},
            {'id': 2, 'name': 'maple'},
            {'id': 3, 'name': 'oak'},
        ]

    def test_wrong_method(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, methods=['GET', 'POST'])
        code, html = self.fetch(
            '/api/tree',
            method="PUT",
            json={
                'objects': [
                    {'id': 1, 'name': 'cedar'},
                    {'id': 2, 'name': 'mango'},
                ]
            },
        )
        assert code == 405

    def test_wrong_url(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree)
        code, html = self.fetch('/apy/trea')
        assert code == 404
