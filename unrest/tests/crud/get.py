from .. import idsorted
from ...unrest import UnRest
from ..model import Fruit, Tree


class GetTestCollection(object):
    def test_get_tree(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree)
        rest(Fruit)
        code, json = self.fetch('/api/tree')
        assert code == 200
        assert json['occurences'] == 3
        assert idsorted(json['objects']) == [
            {'id': 1, 'name': 'pine'},
            {'id': 2, 'name': 'maple'},
            {'id': 3, 'name': 'oak'},
        ]

    def test_get_tree_name(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, name='forest')
        code, json = self.fetch('/api/forest')
        assert code == 200
        assert json['occurences'] == 3
        assert idsorted(json['objects']) == [
            {'id': 1, 'name': 'pine'},
            {'id': 2, 'name': 'maple'},
            {'id': 3, 'name': 'oak'},
        ]

    def test_get_tree_query(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)

        def base_query(q):
            return self.session.query(Tree).filter(Tree.id > 1)

        rest(Tree, query=base_query)
        code, json = self.fetch('/api/tree')
        assert code == 200
        assert json['occurences'] == 2
        assert idsorted(json['objects']) == [
            {'id': 2, 'name': 'maple'},
            {'id': 3, 'name': 'oak'},
        ]

    def test_get_tree_query_factory(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, query=lambda q: q.filter(Tree.id < 2))
        code, json = self.fetch('/api/tree')
        assert code == 200
        assert json['occurences'] == 1
        assert json['primary_keys'] == ['id']
        assert idsorted(json['objects']) == [{'id': 1, 'name': 'pine'}]

    def test_get_fruits(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree)
        rest(Fruit)
        code, json = self.fetch('/api/fruit')
        assert code == 200
        assert json['occurences'] == 5
        assert json['primary_keys'] == ['fruit_id']
        assert idsorted(json['objects'], 'fruit_id') == [
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

    def test_get_fruits_only(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Fruit, only=['color', 'size'])
        code, json = self.fetch('/api/fruit')
        assert code == 200
        assert json['occurences'] == 5
        assert idsorted(json['objects'], 'fruit_id') == [
            {'fruit_id': 1, 'color': 'grey', 'size': 12.0},
            {'fruit_id': 2, 'color': 'darkgrey', 'size': 23.0},
            {'fruit_id': 3, 'color': 'brown', 'size': 2.12},
            {'fruit_id': 4, 'color': 'red', 'size': 0.5},
            {'fruit_id': 5, 'color': 'orangered', 'size': 100.0},
        ]

    def test_get_fruits_exclude(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Fruit, exclude=['color', 'age', 'double_size'])
        code, json = self.fetch('/api/fruit')
        assert code == 200
        assert json['occurences'] == 5
        assert idsorted(json['objects'], 'fruit_id') == [
            {'fruit_id': 1, 'size': 12.0, 'tree_id': 1},
            {'fruit_id': 2, 'size': 23.0, 'tree_id': 1},
            {'fruit_id': 3, 'size': 2.12, 'tree_id': 1},
            {'fruit_id': 4, 'size': 0.5, 'tree_id': 2},
            {'fruit_id': 5, 'size': 100.0, 'tree_id': 2},
        ]

    def test_get_fruits_only_exclude(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Fruit, only=['color', 'size'], exclude=['color', 'age'])
        code, json = self.fetch('/api/fruit')
        assert code == 200
        assert json['occurences'] == 5
        assert idsorted(json['objects'], 'fruit_id') == [
            {'fruit_id': 1, 'size': 12.0},
            {'fruit_id': 2, 'size': 23.0},
            {'fruit_id': 3, 'size': 2.12},
            {'fruit_id': 4, 'size': 0.5},
            {'fruit_id': 5, 'size': 100.0},
        ]

    def test_no_method(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Fruit, methods=[])
        code, html = self.fetch('/api/fruit')
        assert code == 404

    def test_get_custom(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        fruit = rest(Fruit)

        @fruit.declare('GET')
        def get(payload, fruit_id=None):
            return {'Hey': 'Overridden'}

        code, json = self.fetch('/api/fruit')
        assert code == 200
        assert json == {'Hey': 'Overridden'}

    def test_get_custom_extend(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        fruit = rest(Fruit)

        @fruit.declare('GET')
        def get(payload, fruit_id=None):
            rv = fruit.get(payload, fruit_id=fruit_id)
            return {
                'occurences': rv['occurences'],
                'objects': [{'id': obj['fruit_id']} for obj in rv['objects']],
            }

        code, json = self.fetch('/api/fruit')
        assert code == 200
        assert json['occurences'] == 5
        assert idsorted(json['objects']) == [
            {'id': 1},
            {'id': 2},
            {'id': 3},
            {'id': 4},
            {'id': 5},
        ]
