import logging
from tempfile import NamedTemporaryFile

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Float

from unrest import UnRest

from ..model import Base, Fruit, Tree, fill_data

# Init flask
app = Flask(__name__)
f = NamedTemporaryFile()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % f.name

# Init db
db = SQLAlchemy(app)
Base.metadata.drop_all(bind=db.engine)
Base.metadata.create_all(bind=db.engine)
fill_data(db.session)
db.session.remove()

# Init Unrest
rest = UnRest(app, db.session)
fruit = rest(
    Fruit,
    methods=rest.all,
    properties=[rest.Property('square_size', Float())],
    allow_batch=True
)
rest(
    Tree,
    methods=rest.all,
    relationships={'fruits': fruit},
    properties=['fruit_colors'],
    allow_batch=True
)
