import pytest

from .helpers.flask import FlaskClient
from .helpers.http_server import HTTPServerClient
from .helpers.sanic import SanicClient
from .helpers.tornado import TornadoClient


@pytest.fixture(
    scope="session",
    params=[
        pytest.param(FlaskClient, marks=pytest.mark.flask),
        pytest.param(HTTPServerClient, marks=pytest.mark.http_server),
        pytest.param(TornadoClient, marks=pytest.mark.tornado),
        pytest.param(SanicClient, marks=pytest.mark.sanic),
    ],
)
def client_class(request):
    client_class = request.param
    client_class.setUpClass()
    yield client_class
    client_class.tearDownClass()


@pytest.fixture
def client(client_class):
    client = client_class()
    client.setUp()
    yield client
    client.tearDown()
