from functools import wraps

from ..model import Tree


def test_auth_decorator(rest, http):
    def raise_if_id_is_2(fun):
        @wraps(fun)
        def wrapped(payload, id=None):
            if id == 2:
                rest.raise_error(403, 'is is 2')
            return fun(payload, id=id)
        return wrapped

    rest(Tree, methods=rest.all, auth=raise_if_id_is_2)
    assert http.get('/api/tree/1')[0] == 200
    assert http.get('/api/tree/2')[0] == 403
    assert http.put('/api/tree/1', json={'id': 1, 'name': 'cedar'})[0] == 200
    assert http.put('/api/tree/2', json={'id': 1, 'name': 'cedar'})[0] == 403
    assert http.post('/api/tree/1', json={'name': 'cedar'})[0] == 501
    assert http.post('/api/tree/2', json={'name': 'cedar'})[0] == 403
    assert http.delete('/api/tree/1')[0] == 200
    assert http.delete('/api/tree/2')[0] == 403


def test_read_write_decorator(rest, http):
    def raise_if_id_is_1(fun):
        @wraps(fun)
        def wrapped(payload, id=None):
            if id == 1:
                rest.raise_error(403, 'is is 1')
            return fun(payload, id=id)
        return wrapped

    def raise_if_id_is_2(fun):
        @wraps(fun)
        def wrapped(payload, id=None):
            if id == 2:
                rest.raise_error(403, 'is is 2')
            return fun(payload, id=id)
        return wrapped

    rest(Tree, methods=rest.all,
         read_auth=raise_if_id_is_1, write_auth=raise_if_id_is_2)
    assert http.get('/api/tree/1')[0] == 403
    assert http.get('/api/tree/2')[0] == 200
    assert http.put('/api/tree/1', json={'id': 1, 'name': 'cedar'})[0] == 200
    assert http.put('/api/tree/2', json={'id': 1, 'name': 'cedar'})[0] == 403
    assert http.post('/api/tree/1', json={'name': 'cedar'})[0] == 501
    assert http.post('/api/tree/2', json={'name': 'cedar'})[0] == 403
    assert http.delete('/api/tree/1')[0] == 200
    assert http.delete('/api/tree/2')[0] == 403


def test_all_decorator(rest, http):
    def raise_if_id_is_1(fun):
        @wraps(fun)
        def wrapped(payload, id=None):
            if id == 1:
                rest.raise_error(403, 'is is 1')
            return fun(payload, id=id)
        return wrapped

    def raise_if_id_is_2(fun):
        @wraps(fun)
        def wrapped(payload, id=None):
            if id == 2:
                rest.raise_error(403, 'is is 2')
            return fun(payload, id=id)
        return wrapped

    def raise_if_id_is_3(fun):
        @wraps(fun)
        def wrapped(payload, id=None):
            if id == 3:
                rest.raise_error(403, 'is is 3')
            return fun(payload, id=id)
        return wrapped

    rest(Tree, methods=rest.all,
         read_auth=raise_if_id_is_1, write_auth=raise_if_id_is_2,
         auth=raise_if_id_is_3)
    assert http.get('/api/tree/1')[0] == 403
    assert http.get('/api/tree/2')[0] == 200
    assert http.get('/api/tree/3')[0] == 403
    assert http.put('/api/tree/1', json={'id': 1, 'name': 'cedar'})[0] == 200
    assert http.put('/api/tree/2', json={'id': 1, 'name': 'cedar'})[0] == 403
    assert http.put('/api/tree/3', json={'id': 1, 'name': 'cedar'})[0] == 403
    assert http.post('/api/tree/1', json={'name': 'cedar'})[0] == 501
    assert http.post('/api/tree/2', json={'name': 'cedar'})[0] == 403
    assert http.post('/api/tree/3', json={'name': 'cedar'})[0] == 403
    assert http.delete('/api/tree/1')[0] == 200
    assert http.delete('/api/tree/2')[0] == 403
    assert http.delete('/api/tree/3')[0] == 403
