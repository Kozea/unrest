import os

from sanic import Sanic, response
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import Float

from unrest import UnRest
from unrest.framework.sanic import SanicFramework
from unrest.tests.model import Base, Fruit, Tree, fill_data

app = Sanic()

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


@app.route("/")
async def home(request):
    return response.text("A normal sanic route!")


@app.middleware('response')
async def after_request(request, response):
    session.remove()


rest = UnRest(app, session, framework=SanicFramework)
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

app.run()
