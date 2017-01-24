# unrest
### A troubling rest api library for sqlalchemy models

## This is a work in progress

## Simple sqlalchemy rest api generation.

### Usage (Flask, Tornado, ...)


```python

from unrest import UnRest
rest = UnRest(app)

###

from .model import Person

rest(Person, only=['name', 'sex', 'age'])
```

This should provides you a `/api/person` and a `/api/person/<login>` route accessible in GET only.

To activate data modification, set the methods array like this:

```python

rest(Person, only=['name', 'sex', 'age'], methods=['GET', 'PUT', 'POST', 'DELETE'])
```
You will get both routes on the four methods. Please see [the wikipedia page](https://en.wikipedia.org/wiki/Representational_state_transfer#Relationship_between_URL_and_HTTP_methods) for their signification.
