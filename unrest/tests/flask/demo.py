from tempfile import NamedTemporaryFile

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import Float

from unrest import UnRest, __about__

from ..model import Base, Fruit, Tree, fill_data

# Init flask
app = Flask(__name__)
f = NamedTemporaryFile()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % f.name


# Enable CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add(
        'Access-Control-Allow-Headers', 'Content-Type,Authorization'
    )
    response.headers.add(
        'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS'
    )
    return response


# Init db
db = SQLAlchemy(app)
Base.metadata.drop_all(bind=db.engine)
Base.metadata.create_all(bind=db.engine)
fill_data(db.session)
db.session.remove()

# Optional info mapping (useful to enrich openapi file)
info = {
    'description':
        '''# Unrest demo
This is the demo of unrest api.
This api expose the `Tree` and `Fruit` entity Rest methods.
''',
    'contact': {
        'name': __about__.__author__,
        'url': __about__.__uri__,
        'email': __about__.__email__
    },
    'license': {
        'name': __about__.__license__
    }
}

# Init Unrest
rest = UnRest(app, db.session, info=info)
fruit = rest(
    Fruit,
    methods=rest.all,
    properties=[rest.Property('square_size', Float())]
)
rest(
    Tree,
    methods=rest.all,
    relationships={'fruits': fruit},
    properties=['fruit_colors'],
    allow_batch=True
)
