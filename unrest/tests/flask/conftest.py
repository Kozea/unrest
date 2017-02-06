
import json
from tempfile import NamedTemporaryFile

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy

from unrest import UnRest

from ..model import Base, fill_data


class HTTPClient(FlaskClient):
    def open(self, *args, **kwargs):
        json_data = kwargs.pop('json', '')
        if json_data:
            kwargs.setdefault('data', json.dumps(json_data))
            kwargs.setdefault('content_type', 'application/json')

        response = super(HTTPClient, self).open(*args, **kwargs)

        if response.content_type == 'application/json':
            rv = json.loads(response.data.decode('utf-8'))
        else:
            rv = {'html': response.data.decode('utf-8')}
        return response.status_code, rv


@pytest.fixture
def app(request):
    app = Flask(__name__)
    app.test_client_class = HTTPClient
    f = NamedTemporaryFile()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % f.name
    return app


@pytest.fixture
def http(app):
    return app.test_client()


@pytest.fixture
def db_init(app):
    db = SQLAlchemy(app)
    Base.metadata.drop_all(bind=db.engine)
    return db


@pytest.fixture
def db(request, db_init):
    db = db_init
    Base.metadata.create_all(bind=db.engine)

    fill_data(db.session)
    db.session.remove()

    def drop_all():
        Base.metadata.drop_all(bind=db.engine)

    request.addfinalizer(drop_all)
    return db


@pytest.fixture
def rest(app, db):
    return UnRest(app, db.session)
