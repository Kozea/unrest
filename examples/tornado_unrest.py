import os

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import Float
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from unrest import UnRest
from unrest.framework.tornado import TornadoFramework
from unrest.tests.model import Base, Fruit, Tree, fill_data


class MainHandler(RequestHandler):
    def get(self):
        self.write("A normal tornado route!")


app = Application([(r"/", MainHandler)])
app.listen(8888)

sqlite_db = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'unrest-test.db'
)
db_url = 'sqlite:///%s' % sqlite_db

engine = create_engine(db_url)
Session = sessionmaker()
Session.configure(bind=engine)
session = scoped_session(Session)

if not os.path.exists(sqlite_db):
    Base.metadata.create_all(bind=engine)
    fill_data(session)


rest = UnRest(app, session, framework=TornadoFramework)
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

IOLoop.current().start()
