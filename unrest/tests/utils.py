import json as jsonlib
from tempfile import NamedTemporaryFile

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from . import idsorted
from ..unrest import UnRest
from .model import Base, Fruit, Tree, fill_data

f = NamedTemporaryFile()
db_url = 'sqlite:///%s' % f.name

engine = create_engine(db_url)
Session = sessionmaker()
Session.configure(bind=engine)
session = scoped_session(Session)


class UnRestTestCase(object):
    def setUp(self):
        super().setUp()
        self.engine = engine
        self.session = session
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        fill_data(self.session)

    def tearDown(self):
        self.session.remove()

    def json_fetch(self, *args, **kwargs):
        kwargs.setdefault('method', 'GET')
        json = kwargs.pop('json', '')
        if json:
            kwargs.setdefault('body', jsonlib.dumps(json))
            kwargs.setdefault('headers', {'Content-Type': 'application/json'})

        response = self.fetch(*args, **kwargs)
        code = response.code
        self.assertEqual(
            response.headers.get('Content-Type'), 'application/json'
        )
        rv = jsonlib.loads(response.body.decode('utf-8'))
        return code, rv


class MiscTests(object):
    def test_homepage(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree)
        rest(Fruit)
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'A normal route!')

    def test_get(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree)
        rest(Fruit)
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

    def test_get_name(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, name='forest')

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

    def test_get_fruits(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree)
        rest(Fruit)
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

    def test_post(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        rest(Tree, methods=['GET', 'POST'])
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

    def test_options(self):
        rest = UnRest(self.app, self.session, framework=self.__framework__)
        fruit = rest(Fruit)
        rest(
            Tree,
            methods=rest.all,
            relationships={'fruits': fruit},
            properties=['fruit_colors'],
            allow_batch=True,
        )
        code, json = self.json_fetch('/api/fruit', method='OPTIONS')
        self.assertEqual(code, 200)
        self.assertEqual(
            json,
            {
                'model': 'Fruit',
                'description': 'A bag of fruit',
                'batch': False,
                'parameters': ['fruit_id'],
                'columns': {
                    'age': 'timedelta',
                    'color': 'str',
                    'fruit_id': 'int',
                    'size': 'Decimal',
                    'tree_id': 'int',
                    'double_size': 'Decimal',
                },
                'properties': {},
                'relationships': {},
                'methods': ['GET', 'OPTIONS'],
            },
        )
