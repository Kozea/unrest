# unrest - <small>Simple sqlalchemy rest api generation.</small>


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
rest(Person, only=['name', 'sex', 'age'], methods=['GET', 'PUT', 'POST', 'DELETE', 'PATCH']) # or simply methods=rest.all
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

## Documentation

Full documentation can be found at [kozea.github.io/unrest](https://kozea.github.io/unrest/)

## Example

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
rest(Tree, methods=rest.all, allow_batch=True)
# Don't authorize batch for fruits
rest(Fruit, methods=rest.all)

# Run the app
app.run(debug=True)
```

You will now have:

## GET

### With primary keys arguments
```json
$ curl -s http://localhost:5000/api/tree/1

200 OK
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

```json
$ curl -s http://localhost:5000/api/fruit/1

200 OK
{
    "occurences": 1,
    "objects": [
        {
            "fruit_id": 1,
            "color": "grey",
            "size": 12.0,
            "age": 1041300.0,
            "tree_id": 1
        }
    ]
}
```

### Without argument

```json
$ curl -s http://localhost:5000/api/tree

200 OK
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

```json
$ curl -s http://localhost:5000/api/fruit

200 OK
{
    "occurences": 5,
    "objects": [
        {
            "fruit_id": 1,
            "color": "grey",
            "size": 12.0,
            "age": 1041300.0,
            "tree_id": 1
        },
        {
            "fruit_id": 2,
            "color": "darkgrey",
            "size": 23.0,
            "age": 4233830.213,
            "tree_id": 1
        },
        {
            "fruit_id": 3,
            "color": "brown",
            "size": 2.12,
            "age": 0.0,
            "tree_id": 1
        },
        {
            "fruit_id": 4,
            "color": "red",
            "size": 0.5,
            "age": 2400.0,
            "tree_id": 2
        },
        {
            "fruit_id": 5,
            "color": "orangered",
            "size": 100.0,
            "age": 7200.000012,
            "tree_id": 2
        }
    ]
}
```

## PUT

### With primary keys arguments

```json
$ curl -s http://localhost:5000/api/tree/1 -X PUT -H "Content-Type: application/json" -d '{
  "name": "cedar"
}'

200 OK
{
    "occurences": 1,
    "objects": [
        {
            "id": 1,
            "name": "cedar"
        }
    ]
}
```
Get it again to be sure:

```json
$ curl -s http://localhost:5000/api/tree/1

200 OK
{
    "occurences": 1,
    "objects": [
        {
            "id": 1,
            "name": "cedar"
        }
    ]
}
```

### Without argument

```json
$ curl -s http://localhost:5000/api/tree -X PUT -H "Content-Type: application/json" -d '{
  "objects": [{"id": 2, "name": "cedar"}, {"id": 22, "name": "mango"}]
}'

200 OK
{
    "occurences": 2,
    "objects": [
        {
            "id": 2,
            "name": "cedar"
        },
        {
            "id": 22,
            "name": "mango"
        }
    ]
}
```

Get it again to be sure:

```json
$ curl -s http://localhost:5000/api/tree

200 OK
{
    "occurences": 2,
    "objects": [
        {
            "id": 2,
            "name": "cedar"
        },
        {
            "id": 22,
            "name": "mango"
        }
    ]
}
```

Check that when allow_batch is not set we can't put all:
```json
$ curl -s http://localhost:5000/api/fruit -X PUT -H "Content-Type: application/json" -d '{
  "objects": [
    {"fruit_id": 2, "color": "red"},
    {"fruit_id": 22, "color": "blue"}
  ]
}'

406 Not Acceptable
{
  "message": "You must set allow_batch to True if you want to use batch methods."
}
```

## POST

### With primary keys arguments
```json
$ curl -s http://localhost:5000/api/tree/1 -X POST -H "Content-Type: application/json"

501 Not Implemented
{
  "message": "POST on id corresponds to collection creation. It's not implemented by default. If you want to update an item use the PUT method instead"
}
```

### Without argument
```json
$ curl -s http://localhost:5000/api/fruit -X POST -H "Content-Type: application/json" -d '{
  "color": "forestgreen", "size": 3.14, "age": 1.5926, "tree_id": 3
}'

200 OK
{
    "occurences": 1,
    "objects": [
        {
            "fruit_id": 6,
            "color": "forestgreen",
            "size": 3.14,
            "age": 1.5926,
            "tree_id": 3
        }
    ]
}
```

Now we should have a total of 6 fruits:
```json
$ curl -s http://localhost:5000/api/fruit

200 OK
{
    "occurences": 6,
    "objects": [
        {
            "fruit_id": 1,
            "color": "grey",
            "size": 12.0,
            "age": 1041300.0,
            "tree_id": 1
        },
        {
            "fruit_id": 2,
            "color": "darkgrey",
            "size": 23.0,
            "age": 4233830.213,
            "tree_id": 1
        },
        {
            "fruit_id": 3,
            "color": "brown",
            "size": 2.12,
            "age": 0.0,
            "tree_id": 1
        },
        {
            "fruit_id": 4,
            "color": "red",
            "size": 0.5,
            "age": 2400.0,
            "tree_id": 2
        },
        {
            "fruit_id": 5,
            "color": "orangered",
            "size": 100.0,
            "age": 7200.000012,
            "tree_id": 2
        },
        {
            "fruit_id": 6,
            "color": "forestgreen",
            "size": 3.14,
            "age": 1.5926,
            "tree_id": 3
        }
    ]
}
```

## DELETE

### With primary keys arguments

```json
$ curl -s http://localhost:5000/api/fruit/3 -X DELETE

200 OK
{
    "occurences": 1,
    "objects": [
        {
            "fruit_id": 3,
            "color": "brown",
            "size": 2.12,
            "age": 0.0,
            "tree_id": 1
        }
    ]
}
```

Now we should have only 5 fruits remaining:
```json
$ curl -s http://localhost:5000/api/fruit

200 OK
{
    "occurences": 5,
    "objects": [
        {
            "fruit_id": 1,
            "color": "grey",
            "size": 12.0,
            "age": 1041300.0,
            "tree_id": 1
        },
        {
            "fruit_id": 2,
            "color": "darkgrey",
            "size": 23.0,
            "age": 4233830.213,
            "tree_id": 1
        },
        {
            "fruit_id": 4,
            "color": "red",
            "size": 0.5,
            "age": 2400.0,
            "tree_id": 2
        },
        {
            "fruit_id": 5,
            "color": "orangered",
            "size": 100.0,
            "age": 7200.000012,
            "tree_id": 2
        },
        {
            "fruit_id": 6,
            "color": "forestgreen",
            "size": 3.14,
            "age": 1.5926,
            "tree_id": 3
        }
    ]
}
```

### Without argument

Batch delete is not allowed on fruit:
```json
$ curl -s http://localhost:5000/api/fruit -X DELETE

501 Not Implemented
{
  "message": "You must set allow_batch to True if you want to use batch methods."
}
```
But is on tree:
```json
$ curl -s http://localhost:5000/api/tree -X DELETE

200 OK
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

```json
$ curl -s http://localhost:5000/api/tree

200 OK
{
    "occurences": 0,
    "objects": []
}
```

## PATCH

### With primary keys arguments

```json
$ curl -s http://localhost:5000/api/fruit/1 -X PATCH -H "Content-Type: application/json" -d '{
  "color": "blue"
}'

200 OK
{
    "occurences": 1,
    "objects": [
        {
          "fruit_id": 1,
          "color": "blue",
          "size": 12.0,
          "age": 1041300.0,
          "tree_id": 1
        }
    ]
}
```

### Without argument

```json
$ curl -s http://localhost:5000/api/tree -X PATCH -H "Content-Type: application/json" -d '{
  "objects": [{"id": 2, "name": "cedar"}, {"id": 3, "name": "mango"}]
}'

200 OK
{
    "occurences": 2,
    "objects": [
        {
            "id": 2,
            "name": "cedar"
        },
        {
            "id": 3,
            "name": "mango"
        }
    ]
}
```


Check that when allow_batch is not set we can't put all:
```json
$ curl -s http://localhost:5000/api/fruit -X PATCH -H "Content-Type: application/json" -d '{
  "objects": [
    {"fruit_id": 1, "color": "blue"},
    {"fruit_id": 3, "age": 1038540.0},
    {"fruit_id": 4, "color": "rainbow", "size": 8},
    {"fruit_id": 5, "size": 10, "tree_id": 1}
  ]
}'

406 Not Acceptable
{
  "message": "You must set allow_batch to True if you want to use batch methods."
}
```
otherwise all the specified attributes would have been patched.
