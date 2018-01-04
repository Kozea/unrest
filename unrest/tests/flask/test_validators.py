from datetime import timedelta

from . import idsorted
from ..model import Fruit, Tree


def test_put_tree_validation(rest, http):
    def name_validator(field):
        if len(field.value) > 3:
            raise rest.ValidationError(
                'Name must be shorter than 4 characters.'
            )
        return field.value

    rest(
        Tree,
        methods=['GET', 'PUT'],
        validators={'name': name_validator},
        allow_batch=True
    )
    code, json = http.put(
        '/api/tree',
        json={
            'objects': [{
                'id': 1,
                'name': 'cedar'
            }, {
                'id': 2,
                'name': 'mango'
            }]
        }
    )
    assert code == 500
    assert json['message'] == 'Validation Error'
    assert json['errors'] == [{
        'id': 1,
        'fields': {
            'name': 'Name must be shorter than 4 characters.'
        },
    }, {
        'id': 2,
        'fields': {
            'name': 'Name must be shorter than 4 characters.'
        },
    }]
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {
            'id': 1,
            'name': 'pine'
        },
        {
            'id': 2,
            'name': 'maple'
        },
        {
            'id': 3,
            'name': 'oak'
        },
    ]


def test_put_pk_tree_validation(rest, http):
    def name_validator(field):
        if len(field.value) > 3:
            raise rest.ValidationError(
                'Name must be shorter than 4 characters.'
            )
        return field.value

    rest(Tree, methods=['GET', 'PUT'], validators={'name': name_validator})
    code, json = http.put('/api/tree/1', json={'id': 1, 'name': 'cedar'})
    assert code == 500
    assert json['message'] == 'Validation Error'
    assert json['errors'] == [{
        'id': 1,
        'fields': {
            'name': 'Name must be shorter than 4 characters.'
        },
    }]
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {
            'id': 1,
            'name': 'pine'
        },
        {
            'id': 2,
            'name': 'maple'
        },
        {
            'id': 3,
            'name': 'oak'
        },
    ]


def test_put_pk_tree_validation_ok(rest, http):
    def name_validator(field):
        if len(field.value) > 3:
            raise rest.ValidationError(
                'Name must be shorter than 4 characters.'
            )
        return field.value

    rest(Tree, methods=['GET', 'PUT'], validators={'name': name_validator})
    code, json = http.put('/api/tree/1', json={'id': 1, 'name': 'elm'})
    assert json['occurences'] == 1
    assert idsorted(json['objects']) == [
        {
            'id': 1,
            'name': 'elm'
        },
    ]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {
            'id': 1,
            'name': 'elm'
        },
        {
            'id': 2,
            'name': 'maple'
        },
        {
            'id': 3,
            'name': 'oak'
        },
    ]


def test_post_tree_validation(rest, http):
    def name_validator(field):
        if len(field.value) > 3:
            raise rest.ValidationError(
                'Name must be shorter than 4 characters.'
            )
        return field.value

    rest(Tree, methods=['GET', 'POST'], validators={'name': name_validator})
    code, json = http.post('/api/tree', json={'name': 'mango'})
    assert code == 500
    assert json['message'] == 'Validation Error'
    assert json['errors'] == [{
        'id': None,
        'fields': {
            'name': 'Name must be shorter than 4 characters.'
        },
    }]

    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {
            'id': 1,
            'name': 'pine'
        },
        {
            'id': 2,
            'name': 'maple'
        },
        {
            'id': 3,
            'name': 'oak'
        },
    ]


def test_put_fruit_dual_validation(rest, http):
    def color_validator(field):
        if field.previous.color == 'brown':
            raise field.ValidationError(
                'A brown fruit cannot become %s' % field.value
            )
        return field.value

    def size_validator(field):
        if field.value > 48.9 and field.next.age < timedelta(weeks=2):
            raise rest.ValidationError('Fruit too big for its age')
        return field.value

    def age_validator(field):
        if field.value < timedelta(days=100):
            raise field.ValidationError('Fruit too old')
        return field.value

    def tree_id_validator(field):
        if field.value == 0:
            raise rest.ValidationError('Invalid tree_id')
        return field.value

    rest(
        Fruit,
        methods=['GET', 'PUT'],
        validators={
            'color': color_validator,
            'size': size_validator,
            'age': age_validator,
            'tree_id': tree_id_validator
        }
    )
    code, json = http.put(
        '/api/fruit/3',
        json={
            'fruit_id': 3,
            'color': 'green',
            'size': 50.2,
            'age': 0,
            'tree_id': 0
        }
    )
    assert code == 500
    assert json['message'] == 'Validation Error'
    assert json['errors'] == [{
        'fruit_id': 3,
        'fields': {
            'color': 'A brown fruit cannot become green',
            'size': 'Fruit too big for its age',
            'age': 'Fruit too old',
            'tree_id': 'Invalid tree_id',
        },
    }]


def test_validation_error_code(rest, http):
    def name_validator(field):
        if len(field.value) > 3:
            raise rest.ValidationError(
                'Name must be shorter than 4 characters.'
            )
        return field.value

    rest(
        Tree,
        methods=['GET', 'PUT'],
        validators={'name': name_validator},
        validation_error_code=202
    )
    code, json = http.put('/api/tree/1', json={'id': 1, 'name': 'cedar'})
    assert code == 202
    assert json['message'] == 'Validation Error'
    assert json['errors'] == [{
        'id': 1,
        'fields': {
            'name': 'Name must be shorter than 4 characters.'
        },
    }]
    code, json = http.get('/api/tree')
    assert code == 200
    assert json['occurences'] == 3
    assert idsorted(json['objects']) == [
        {
            'id': 1,
            'name': 'pine'
        },
        {
            'id': 2,
            'name': 'maple'
        },
        {
            'id': 3,
            'name': 'oak'
        },
    ]
