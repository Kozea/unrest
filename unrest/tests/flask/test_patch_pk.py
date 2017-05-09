from ..model import Tree


def test_patch_tree(rest, http):
    rest(Tree, methods=['GET', 'PATCH'])
    code, json = http.patch('/api/tree/1', json={'id': 1, 'name': 'cedar'})
    assert code == 406
