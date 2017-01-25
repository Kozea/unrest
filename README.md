# unrest
## A troubling rest api library for sqlalchemy models


*Simple sqlalchemy rest api generation.*


```python
from unrest import UnRest
rest = UnRest(app)  # Flask app or a tornado application (coming soon) or anything else (you will have to implement the framework class)

from .model import Person

rest(Person, only=['name', 'sex', 'age'])
```

This should provides you a `/api/person` and a `/api/person/<login>` route accessible in GET only.

To activate data modification, set the methods array like this:

```python
rest(Person, only=['name', 'sex', 'age'], methods=['GET', 'PUT', 'POST', 'DELETE'])
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
