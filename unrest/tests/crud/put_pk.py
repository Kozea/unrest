from .. import idsorted
from ...unrest import UnRest
from ..model import Fruit, Tree


class PutPkTestCollection(object):
    def test_put_tree(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, methods=['GET', 'PUT'])
        code, json = self.fetch(
            '/api/tree/1', method="PUT", json={'id': 1, 'name': 'cedar'}
        )
        assert code == 200
        assert json['occurences'] == 1
        assert idsorted(json['objects']) == [{'id': 1, 'name': 'cedar'}]

        code, json = self.fetch('/api/tree')
        assert code == 200
        assert json['occurences'] == 3
        assert idsorted(json['objects']) == [
            {'id': 1, 'name': 'cedar'},
            {'id': 2, 'name': 'maple'},
            {'id': 3, 'name': 'oak'},
        ]

    def test_put_tree_without_id(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, methods=['GET', 'PUT'])
        code, json = self.fetch(
            '/api/tree/1', method="PUT", json={'name': 'cedar'}
        )
        assert code == 200
        assert json['occurences'] == 1
        assert idsorted(json['objects']) == [{'id': 1, 'name': 'cedar'}]

        code, json = self.fetch('/api/tree')
        assert code == 200
        assert json['occurences'] == 3
        assert idsorted(json['objects']) == [
            {'id': 1, 'name': 'cedar'},
            {'id': 2, 'name': 'maple'},
            {'id': 3, 'name': 'oak'},
        ]

    def test_put_tree_unexisting(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, methods=['GET', 'PUT'])
        code, json = self.fetch(
            '/api/tree/4', method="PUT", json={'name': 'palm'}
        )
        assert code == 200
        assert json['occurences'] == 1
        assert idsorted(json['objects']) == [{'id': 4, 'name': 'palm'}]

        code, json = self.fetch('/api/tree')
        assert code == 200
        assert json['occurences'] == 4
        assert idsorted(json['objects']) == [
            {'id': 1, 'name': 'pine'},
            {'id': 2, 'name': 'maple'},
            {'id': 3, 'name': 'oak'},
            {'id': 4, 'name': 'palm'},
        ]

    def test_put_tree_with_another_id(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, methods=['GET', 'PUT'])
        code, html = self.fetch(
            '/api/tree/1', method="PUT", json={'id': 5, 'name': 'cedar'}
        )
        assert code == 500

    def test_put_fruit(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Fruit, methods=['GET', 'PUT'])
        code, json = self.fetch(
            '/api/fruit/1', method="PUT", json={'fruit_id': 1, 'color': 'blue'}
        )
        assert code == 200
        assert json['occurences'] == 1
        assert idsorted(json['objects'], 'fruit_id') == [
            {
                'fruit_id': 1,
                'color': 'blue',
                'size': None,
                'double_size': None,
                'age': None,
                'tree_id': None,
            }
        ]

        code, json = self.fetch('/api/fruit')
        assert code == 200
        assert json['occurences'] == 5
        assert idsorted(json['objects'], 'fruit_id') == [
            {
                'fruit_id': 1,
                'color': 'blue',
                'size': None,
                'double_size': None,
                'age': None,
                'tree_id': None,
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
                'tree_id': 2,
            },
        ]
