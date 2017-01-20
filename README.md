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
