from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from ...framework.flask import FlaskFramework
from .unrest_client import UnRestClient, implement_sqlite_regexp


class FlaskClient(UnRestClient):
    __framework__ = FlaskFramework

    @classmethod
    def db(cls):
        cls.db_url = 'sqlite://'

    def setUp(self):
        self.get_app()
        self.db = SQLAlchemy(self.app)
        self.engine = self.db.engine
        implement_sqlite_regexp(self.engine)
        self.session = self.db.session
        super().setUp()

    def get_app(self):
        app = Flask(__name__)

        @app.route('/')
        def index():
            return 'A normal route!'

        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = self.db_url
        self.app = app
        self.opener = app.test_client()
        return app

    def raw_fetch(self, url, method='GET', headers={}, body=None):
        response = self.opener.open(
            url, method=method, headers=headers, data=body
        )
        response.code = response.status_code
        response.body = response.data
        return response
