from .. import idsorted
from ...unrest import UnRest
from ..model import Fruit, Tree


class PutTestCollection(object):
    def test_put_tree_implicitly_unallowed(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, methods=['GET', 'PUT'])
        code, html = self.fetch(
            '/api/tree', method="PUT", json={'id': 1, 'name': 'cedar'}
        )
        assert code == 406

    def test_put_tree(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, methods=['GET', 'PUT'], allow_batch=True)
        code, json = self.fetch(
            '/api/tree',
            method="PUT",
            json={
                'objects': [
                    {'id': 1, 'name': 'cedar'},
                    {'id': 2, 'name': 'mango'},
                ]
            },
        )
        assert code == 200
        assert json['occurences'] == 2
        assert idsorted(json['objects']) == [
            {'id': 1, 'name': 'cedar'},
            {'id': 2, 'name': 'mango'},
        ]

        code, json = self.fetch('/api/tree')
        assert code == 200
        assert json['occurences'] == 2
        assert idsorted(json['objects']) == [
            {'id': 1, 'name': 'cedar'},
            {'id': 2, 'name': 'mango'},
        ]

    def test_put_with_defaults(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(
            Fruit,
            methods=['GET', 'PUT'],
            allow_batch=True,
            defaults={'color': 'white', 'age': lambda p: p['size'] * 2},
        )
        code, json = self.fetch(
            '/api/fruit',
            method="PUT",
            json={
                'objects': [
                    {'size': 1.0, 'tree_id': 1},
                    {'color': 'yellow', 'size': 2.0, 'tree_id': 2},
                ]
            },
        )
        assert code == 200
        assert json['occurences'] == 2
        assert idsorted(json['objects'], 'fruit_id') == [
            {
                'fruit_id': 1,
                'color': 'white',
                'size': 1.0,
                'double_size': 2.0,
                'age': 2.0,
                'tree_id': 1,
            },
            {
                'fruit_id': 2,
                'color': 'yellow',
                'size': 2.0,
                'double_size': 4.0,
                'age': 4.0,
                'tree_id': 2,
            },
        ]

        code, json = self.fetch('/api/fruit')
        assert code == 200
        assert json['occurences'] == 2
        assert idsorted(json['objects'], 'fruit_id') == [
            {
                'fruit_id': 1,
                'color': 'white',
                'size': 1.0,
                'double_size': 2.0,
                'age': 2.0,
                'tree_id': 1,
            },
            {
                'fruit_id': 2,
                'color': 'yellow',
                'size': 2.0,
                'double_size': 4.0,
                'age': 4.0,
                'tree_id': 2,
            },
        ]

    def test_put_with_fixed(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(
            Fruit,
            methods=['GET', 'PUT'],
            allow_batch=True,
            fixed={'color': 'white', 'age': lambda p: p['size'] * 2},
        )
        code, json = self.fetch(
            '/api/fruit',
            method="PUT",
            json={
                'objects': [
                    {'size': 1.0, 'tree_id': 1},
                    {'color': 'yellow', 'size': 2.0, 'tree_id': 2},
                ]
            },
        )
        assert code == 200
        assert json['occurences'] == 2
        assert idsorted(json['objects'], 'fruit_id') == [
            {
                'fruit_id': 1,
                'color': 'white',
                'size': 1.0,
                'double_size': 2.0,
                'age': 2.0,
                'tree_id': 1,
            },
            {
                'fruit_id': 2,
                'color': 'white',
                'size': 2.0,
                'double_size': 4.0,
                'age': 4.0,
                'tree_id': 2,
            },
        ]

        code, json = self.fetch('/api/fruit')
        assert code == 200
        assert json['occurences'] == 2
        assert idsorted(json['objects'], 'fruit_id') == [
            {
                'fruit_id': 1,
                'color': 'white',
                'size': 1.0,
                'double_size': 2.0,
                'age': 2.0,
                'tree_id': 1,
            },
            {
                'fruit_id': 2,
                'color': 'white',
                'size': 2.0,
                'double_size': 4.0,
                'age': 4.0,
                'tree_id': 2,
            },
        ]
