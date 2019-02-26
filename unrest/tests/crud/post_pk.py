from .. import idsorted
from ...unrest import UnRest
from ..model import Tree


class PostPkTestCollection(object):
    def test_post_tree_with_pk(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, methods=['GET', 'POST'])
        code, json = self.fetch(
            '/api/tree/6', method="POST", json={'name': 'mango'}
        )
        assert code == 501

    def test_post_tree_with_pk_custom(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        tree = rest(Tree)

        @tree.declare('POST')
        def post(payload, id=None):
            # Make it work anyway
            return tree.post(payload)

        code, json = self.fetch(
            '/api/tree/9', method="POST", json={'name': 'mango'}
        )
        assert code == 200
        assert json['occurences'] == 1
        assert idsorted(json['objects']) == [{'id': 4, 'name': 'mango'}]

        code, json = self.fetch('/api/tree')
        assert json['occurences'] == 4
        assert idsorted(json['objects']) == [
            {'id': 1, 'name': 'pine'},
            {'id': 2, 'name': 'maple'},
            {'id': 3, 'name': 'oak'},
            {'id': 4, 'name': 'mango'},
        ]