import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Float

from unrest import UnRest
from unrest.idiom.yaml import YamlIdiom
from unrest.tests.model import Base, Fruit, Tree, fill_data

app = Flask(__name__)

sqlite_db = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'unrest-test.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_db}'

db = SQLAlchemy(app)

if not os.path.exists(sqlite_db):
    Base.metadata.create_all(bind=db.engine)
    fill_data(db.session)
    db.session.remove()


@app.route("/")
def home():
    return "A normal flask route!"


rest = UnRest(app, db.session, idiom=YamlIdiom)
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
