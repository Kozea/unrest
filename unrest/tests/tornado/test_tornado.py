import json as jsonlib
import os
from tempfile import NamedTemporaryFile

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import Float
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application, RequestHandler

from . import idsorted
from ...framework.tornado import TornadoFramework
from ...unrest import UnRest
from ..model import Base, Fruit, Tree, fill_data


def make_app(make_unrest):
    class MainHandler(RequestHandler):
        def get(self):
            self.write("A normal tornado route!")

    app = Application([(r"/", MainHandler)])

    f = NamedTemporaryFile()
    db_url = 'sqlite:///%s' % f.name

    engine = create_engine(db_url)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = scoped_session(Session)

    if os.path.exists(db_url):
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    fill_data(session)
    app._engine = engine
    app._session = session
    make_unrest(app, session)

    return app


def make_default_unrest(app, session):
    rest = UnRest(app, session, framework=TornadoFramework)
    fruit = rest(
        Fruit,
        methods=rest.all,
        properties=[rest.Property('square_size', Float())],
    )
    rest(
        Tree,
        methods=rest.all,
        relationships={'fruits': fruit},
        properties=['fruit_colors'],
        allow_batch=True,
    )
    return rest


class UnrestTornadoTestCase(AsyncHTTPTestCase):
    def setUp(self):
        super().setUp()
        Base.metadata.drop_all(bind=self._app._engine)
        Base.metadata.create_all(bind=self._app._engine)
        fill_data(self._app._session)

    def get_app(self):
        return make_app(self.make_unrest)

    def make_unrest(self, app, session):
        return make_default_unrest(app, session)

    def json_fetch(self, *args, **kwargs):
        kwargs.setdefault('method', 'GET')
        json = kwargs.pop('json', '')
        if json:
            kwargs.setdefault('body', jsonlib.dumps(json))
            kwargs.setdefault('headers', {'content-type': 'application/json'})

        response = self.fetch(*args, **kwargs)
        code = response.code
        self.assertEqual(
            response.headers.get('content-type'), 'application/json'
        )
        rv = jsonlib.loads(response.body.decode('utf-8'))
        return code, rv


class TestTornadoHome(UnrestTornadoTestCase):
    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'A normal tornado route!')


class TestTornadoGet(UnrestTornadoTestCase):
    def make_unrest(self, app, session):
        rest = UnRest(app, session, framework=TornadoFramework)
        rest(Tree)
        rest(Fruit)

    def test_get(self):
        code, json = self.json_fetch('/api/tree')
        self.assertEqual(code, 200)
        self.assertEqual(json['occurences'], 3)
        self.assertEqual(
            idsorted(json['objects']),
            [
                {'id': 1, 'name': 'pine'},
                {'id': 2, 'name': 'maple'},
                {'id': 3, 'name': 'oak'},
            ],
        )


class TestTornadoGetName(UnrestTornadoTestCase):
    def make_unrest(self, app, session):
        rest = UnRest(app, session, framework=TornadoFramework)
        rest(Tree, name='forest')

    def test_get_name(self):
        code, json = self.json_fetch('/api/forest')
        self.assertEqual(code, 200)
        self.assertEqual(json['occurences'], 3)
        self.assertEqual(
            idsorted(json['objects']),
            [
                {'id': 1, 'name': 'pine'},
                {'id': 2, 'name': 'maple'},
                {'id': 3, 'name': 'oak'},
            ],
        )


class TestTornadoGetFruits(UnrestTornadoTestCase):
    def make_unrest(self, app, session):
        rest = UnRest(app, session, framework=TornadoFramework)
        rest(Fruit)

    def test_get_fruits(self):
        code, json = self.json_fetch('/api/fruit')
        self.assertEqual(code, 200)
        self.assertEqual(json['occurences'], 5)
        self.assertEqual(json['primary_keys'], ['fruit_id'])
        self.assertEqual(
            idsorted(json['objects'], 'fruit_id'),
            [
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
            ],
        )


class TestTornadoPost(UnrestTornadoTestCase):
    def make_unrest(self, app, session):
        rest = UnRest(app, session, framework=TornadoFramework)
        rest(Tree, methods=['GET', 'POST'])

    def test_post(self):
        code, json = self.json_fetch(
            '/api/tree', method='POST', json={'name': 'cedar'}
        )
        self.assertEqual(code, 200)
        self.assertEqual(json['occurences'], 1)
        self.assertEqual(
            idsorted(json['objects']), [{'id': 4, 'name': 'cedar'}]
        )

        code, json = self.json_fetch('/api/tree')
        self.assertEqual(code, 200)
        self.assertEqual(json['occurences'], 4)
        self.assertEqual(
            idsorted(json['objects']),
            [
                {'id': 1, 'name': 'pine'},
                {'id': 2, 'name': 'maple'},
                {'id': 3, 'name': 'oak'},
                {'id': 4, 'name': 'cedar'},
            ],
        )
