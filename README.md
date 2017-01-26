# unrest

### Simple sqlalchemy rest api generation.


```python
from unrest import UnRest
# First, initialize UnRest with your web application
rest = UnRest(app)

# Then declare your endpoint
rest(Person)
```

This should provides you a `/api/person` and a `/api/person/<login>` route accessible in GET only.

To activate data modification, set the methods array like this:

```python
rest(Person, only=['name', 'sex', 'age'], methods=['GET', 'PUT', 'POST', 'DELETE']) # or simply methods=rest.all
```

You will get both routes on the four methods. Please see [the wikipedia page](https://en.wikipedia.org/wiki/Representational_state_transfer#Relationship_between_URL_and_HTTP_methods) for their signification.

You can also override the default methods like this:

```python
person = rest(Person)

@person.declare('GET')
def get(payload, login=None):
    # Pre get hook
    if login:
        login = login.upper()
    rv = person.get(payload, login=login)
    # Post get hook
    return {
        'occurences': rv['occurences'],
        'objects': [
            {'login': person['login'].lower()} for person in rv['objects']
        ]
    }
```

### Example

Consider this simple web application:

```python
from datetime import timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Interval, Numeric, String

from unrest import UnRest

# Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/unrest.db'

# Model definition
db = SQLAlchemy(app)

class Tree(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)

    @property
    def fruit_colors(self):
        return ', '.join([fruit.color for fruit in self.fruits])

class Fruit(db.Model):
    fruit_id = Column(Integer, primary_key=True)
    color = Column(String(50))
    size = Column(Numeric)
    age = Column(Interval)
    tree_id = Column(Integer, ForeignKey('tree.id'))
    tree = relationship(Tree, backref='fruits')

# Drop everything just in case
db.drop_all()

# Create model
db.create_all()

# Data insertion
pine = Tree(name='pine')
maple = Tree(name='maple')
oak = Tree(name='oak')
db.session.add(pine)
db.session.add(maple)
db.session.add(oak)

db.session.add(Fruit(color='grey', size=12, age=timedelta(days=12, hours=1, minutes=15), tree=pine))
db.session.add(Fruit(color='darkgrey', size=23, age=timedelta(days=49, seconds=230, milliseconds=213), tree=pine))
db.session.add(Fruit(color='brown', size=2.12, age=timedelta(0), tree=pine))
db.session.add(Fruit(color='red', size=.5, age=timedelta(minutes=40), tree=maple))
db.session.add(Fruit(color='orangered', size=100, age=timedelta(hours=2, microseconds=12), tree=maple))

db.session.commit()
db.session.remove()

# Declare rest endpoints
rest = UnRest(app, db.session)

# Authorize every methods
rest(Tree, methods=rest.all)
# Authorize batch for fruit
rest(Fruit, methods=rest.all, allow_batch=True)

# Run the app
app.run(debug=True)
```

You will now have:

#### Get all

`$ curl -s http://localhost:5000/api/tree`
```json
{
    "occurences": 3,
    "objects": [
        {
            "id": 1,
            "name": "pine"
        },
        {
            "id": 2,
            "name": "maple"
        },
        {
            "id": 3,
            "name": "oak"
        }
    ]
}
```

#### Get one
`$ curl -s http://localhost:5000/api/tree/1`
```json
{
    "occurences": 1,
    "objects": [
        {
            "id": 1,
            "name": "pine"
        }
    ]
}
```
