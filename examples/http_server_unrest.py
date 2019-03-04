import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import Float

from unrest import UnRest
from unrest.framework.simple import HTTPServerFramework
from unrest.tests.model import Base, Fruit, Tree, fill_data


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'A normal simple http server route!')


httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
sqlite_db = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'unrest-test.db'
)
db_url = f'sqlite:///{sqlite_db}'

engine = create_engine(db_url)
Session = sessionmaker()
Session.configure(bind=engine)
session = scoped_session(Session)

if not os.path.exists(sqlite_db):
    Base.metadata.create_all(bind=engine)
    fill_data(session)
    session.remove()


rest = UnRest(httpd, session, framework=HTTPServerFramework)
fruit = rest(
    Fruit, methods=rest.all, properties=[rest.Property('square_size', Float())]
)
rest(
    Tree,
    methods=rest.all,
    relationships={'fruits': fruit},
    properties=['fruit_colors'],
    allow_batch=True,
)

httpd.serve_forever()
