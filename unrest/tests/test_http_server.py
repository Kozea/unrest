import json as jsonlib
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from tempfile import NamedTemporaryFile
from unittest import TestCase

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import Float

from . import idsorted
from ..framework.http_server import HTTPServerFramework
from ..unrest import UnRest
from .model import Base, Fruit, Tree, fill_data

f = NamedTemporaryFile()
db_url = 'sqlite:///%s' % f.name

engine = create_engine(db_url)
Session = sessionmaker()
Session.configure(bind=engine)
session = scoped_session(Session)


class UnrestHTTPServerTestCase(TestCase):
    def setUp(self):
        super().setUp()

        class FakeApp(object):
            def __init__(self, rhc):
                self.RequestHandlerClass = rhc

        class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'A normal simple http server route!')

        self.app = FakeApp(SimpleHTTPRequestHandler)

        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        fill_data(session)
        self.engine = engine
        self.session = session
        self.make_unrest()

        class FakeRequest(self.app.RequestHandlerClass):
            def __init__(self, request):
                self.rfile = BytesIO()
                self.rfile.write(request)
                self.rfile.seek(0)
                self.wfile = BytesIO()
                self.handle_one_request()

            def log_request(self, code='-', size='-'):
                pass

        self.app.RequestHandlerClass = FakeRequest
        self.rest = self.make_unrest()

    def tearDown(self):
        self.session.remove()

    def make_unrest(self):
        rest = UnRest(self.app, self.session, framework=HTTPServerFramework)
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

    def fetch(self, url, method='GET', headers={}, body=None):
        class FakeResponse(object):
            def __init__(self, code, headers, body):
                self.code = code
                self.headers = headers
                self.body = body

        if body:
            headers['Content-Length'] = len(body)

        request = '\r\n'.join(
            ['%s %s HTTP/1.1' % (method.upper(), url)]
            + ['%s:%s' % (key, value) for key, value in headers.items()]
        )
        if body:
            request += '\r\n\r\n' + body
        print(request)

        server = self.app.RequestHandlerClass(request.encode('iso-8859-1'))
        server.wfile.seek(0)
        res = server.wfile.read().decode('iso-8859-1')
        [head, body] = res.split('\r\n\r\n')
        res_lines = head.split('\r\n')
        [_, code, message] = res_lines[0].split(' ', 2)
        headers = {
            line.split(':')[0]: line.split(':')[1].strip()
            for line in res_lines[1:]
        }

        return FakeResponse(int(code), headers, body.encode('utf-8'))

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


class TestHTTPServerHome(UnrestHTTPServerTestCase):
    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'A normal simple http server route!')


class TestHTTPServerGet(UnrestHTTPServerTestCase):
    def make_unrest(self):
        rest = UnRest(self.app, self.session, framework=HTTPServerFramework)
        rest(Tree)
        rest(Fruit)
        return rest

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


class TestHTTPServerGetName(UnrestHTTPServerTestCase):
    def make_unrest(self):
        rest = UnRest(self.app, self.session, framework=HTTPServerFramework)
        rest(Tree, name='forest')
        return rest

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


class TestHTTPServerGetFruits(UnrestHTTPServerTestCase):
    def make_unrest(self):
        rest = UnRest(self.app, self.session, framework=HTTPServerFramework)
        rest(Fruit)
        return rest

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


class TestHTTPServerPost(UnrestHTTPServerTestCase):
    def make_unrest(self):
        rest = UnRest(self.app, self.session, framework=HTTPServerFramework)
        rest(Tree, methods=['GET', 'POST'])
        return rest

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


class TestHTTPServerOptions(UnrestHTTPServerTestCase):
    def make_unrest(self):
        rest = UnRest(self.app, self.session, framework=HTTPServerFramework)
        fruit = rest(Fruit)
        rest(
            Tree,
            methods=rest.all,
            relationships={'fruits': fruit},
            properties=['fruit_colors'],
            allow_batch=True,
        )
        return rest

    def test_options(self):
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
