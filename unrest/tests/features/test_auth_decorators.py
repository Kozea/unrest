from functools import wraps

from ...unrest import UnRest
from ..model import Tree


def test_auth_decorator(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)

    def raise_if_id_is_2(fun):
        @wraps(fun)
        def wrapped(request, payload, id=None):
            if id == 2:
                rest.raise_error(403, 'is is 2')
            return fun(request, payload, id=id)

        return wrapped

    rest(Tree, methods=rest.all, auth=raise_if_id_is_2)
    assert client.fetch('/api/tree/1')[0] == 200
    assert client.fetch('/api/tree/2')[0] == 403
    assert (
        client.fetch(
            '/api/tree/1', method="PUT", json={'id': 1, 'name': 'cedar'}
        )[0]
        == 200
    )
    assert (
        client.fetch(
            '/api/tree/2', method="PUT", json={'id': 1, 'name': 'cedar'}
        )[0]
        == 403
    )
    assert (
        client.fetch('/api/tree/1', method="POST", json={'name': 'cedar'})[0]
        == 501
    )
    assert (
        client.fetch('/api/tree/2', method="POST", json={'name': 'cedar'})[0]
        == 403
    )
    assert client.fetch('/api/tree/1', method="DELETE")[0] == 200
    assert client.fetch('/api/tree/2', method="DELETE")[0] == 403


def test_read_write_decorator(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)

    def raise_if_id_is_1(fun):
        @wraps(fun)
        def wrapped(request, payload, id=None):
            if id == 1:
                rest.raise_error(403, 'is is 1')
            return fun(request, payload, id=id)

        return wrapped

    def raise_if_id_is_2(fun):
        @wraps(fun)
        def wrapped(request, payload, id=None):
            if id == 2:
                rest.raise_error(403, 'is is 2')
            return fun(request, payload, id=id)

        return wrapped

    rest(
        Tree,
        methods=rest.all,
        read_auth=raise_if_id_is_1,
        write_auth=raise_if_id_is_2,
    )
    assert client.fetch('/api/tree/1')[0] == 403
    assert client.fetch('/api/tree/2')[0] == 200
    assert (
        client.fetch(
            '/api/tree/1', method="PUT", json={'id': 1, 'name': 'cedar'}
        )[0]
        == 200
    )
    assert (
        client.fetch(
            '/api/tree/2', method="PUT", json={'id': 1, 'name': 'cedar'}
        )[0]
        == 403
    )
    assert (
        client.fetch('/api/tree/1', method="POST", json={'name': 'cedar'})[0]
        == 501
    )
    assert (
        client.fetch('/api/tree/2', method="POST", json={'name': 'cedar'})[0]
        == 403
    )
    assert client.fetch('/api/tree/1', method="DELETE")[0] == 200
    assert client.fetch('/api/tree/2', method="DELETE")[0] == 403


def test_all_decorator(client):
    rest = UnRest(client.app, client.session, framework=client.__framework__)

    def raise_if_id_is_1(fun):
        @wraps(fun)
        def wrapped(request, payload, id=None):
            if id == 1:
                rest.raise_error(403, 'is is 1')
            return fun(request, payload, id=id)

        return wrapped

    def raise_if_id_is_2(fun):
        @wraps(fun)
        def wrapped(request, payload, id=None):
            if id == 2:
                rest.raise_error(403, 'is is 2')
            return fun(request, payload, id=id)

        return wrapped

    def raise_if_id_is_3(fun):
        @wraps(fun)
        def wrapped(request, payload, id=None):
            if id == 3:
                rest.raise_error(403, 'is is 3')
            return fun(request, payload, id=id)

        return wrapped

    rest(
        Tree,
        methods=rest.all,
        read_auth=raise_if_id_is_1,
        write_auth=raise_if_id_is_2,
        auth=raise_if_id_is_3,
    )
    assert client.fetch('/api/tree/1')[0] == 403
    assert client.fetch('/api/tree/2')[0] == 200
    assert client.fetch('/api/tree/3')[0] == 403
    assert (
        client.fetch(
            '/api/tree/1', method="PUT", json={'id': 1, 'name': 'cedar'}
        )[0]
        == 200
    )
    assert (
        client.fetch(
            '/api/tree/2', method="PUT", json={'id': 1, 'name': 'cedar'}
        )[0]
        == 403
    )
    assert (
        client.fetch(
            '/api/tree/3', method="PUT", json={'id': 1, 'name': 'cedar'}
        )[0]
        == 403
    )
    assert (
        client.fetch('/api/tree/1', method="POST", json={'name': 'cedar'})[0]
        == 501
    )
    assert (
        client.fetch('/api/tree/2', method="POST", json={'name': 'cedar'})[0]
        == 403
    )
    assert (
        client.fetch('/api/tree/3', method="POST", json={'name': 'cedar'})[0]
        == 403
    )
    assert client.fetch('/api/tree/1', method="DELETE")[0] == 200
    assert client.fetch('/api/tree/2', method="DELETE")[0] == 403
    assert client.fetch('/api/tree/3', method="DELETE")[0] == 403
