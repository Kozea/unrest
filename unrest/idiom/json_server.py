import json
from collections import defaultdict
from itertools import zip_longest

from sqlalchemy import asc, desc, func, or_
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import String

from ..util import Response
from . import Idiom

PK_DELIM = '___'


def universal_re(attr, value, query):
    dbtype = query.session.bind.dialect.__module__.split('.')[2]
    if dbtype == 'postgresql':
        return attr.op('~')(value)  # pragma: no cover
    if dbtype == 'oracle':
        return func.REGEXP_LIKE(attr, value)  # pragma: no cover
    if dbtype in ['sqlite', 'mysql', 'sybase']:
        return attr.op('REGEXP')(value)
    # Hope that a regexp fun exists
    return func.regexp(attr, value)  # pragma: no cover


class JsonServerIdiom(Idiom):
    """
    The [JSON Server](https://github.com/typicode/json-server) idiom
    implementation.

    Currently support all basic queries and first-level (no nested props)
    filter, sort, pagination, slice, operators
    (`_gte`, `_lte`, `_ne`, `_like`)
    and `q` full-text search (which works better with
    [SQLAlchemy-Searchable](https://sqlalchemy-searchable.readthedocs.io))
    """

    def request_to_payload(self, request):
        if request.payload:
            try:
                data = json.loads(request.payload.decode('utf-8'))
            except json.JSONDecodeError as e:
                self.rest.raise_error(400, f'JSON Error in payload: {e}')
            if isinstance(data, list):
                return {'objects': data}
            return data

    def data_to_response(self, data, request, status=200):
        if (
            request.method == 'GET'
            and self.rest.unrest.empty_get_as_404
            and 'occurences' in data
            and data['occurences'] == 0
        ):
            status = 404

        if 'objects' in data:
            objects = data['objects']
            for object in objects:
                for key, relationship in self.rest.relationships.items():
                    object[key] = (
                        [
                            PK_DELIM.join(
                                str(ref[pk])
                                for pk in relationship.primary_keys
                            )
                            for ref in object[key]
                        ]
                        if len(relationship.primary_keys) > 1
                        else [
                            ref[relationship.primary_keys[0]]
                            for ref in object[key]
                        ]
                    )
            # When there's parameter it applies on a unique object
            # except from POST
            if (
                request.parameters
                and all(
                    value is not None for value in request.parameters.values()
                )
                or request.method == 'POST'
            ):
                objects = objects[0]
            payload = json.dumps(objects)
        else:
            payload = json.dumps(data)
        headers = {'Content-Type': 'application/json'}
        if 'occurences' in data:
            headers['X-Total-Count'] = data['occurences']
            headers['Access-Control-Expose-Headers'] = 'X-Total-Count'
        response = Response(payload, headers, status)
        return response

    def alter_query(self, request, query):
        Model = self.rest.Model
        params = defaultdict(str)
        filters = {}
        for param, values in request.query.items():
            if param.startswith('_'):
                params[param[1:]] = values[0]
            elif param == 'q':
                params['q'] = values[0]
            else:
                filters[param] = values

        # Filter
        if filters:
            for key, values in filters.items():
                if len(values) == 1:
                    value = values[0]
                    if key.endswith('_gte'):
                        cond = getattr(Model, key[: -len('_gte')]) >= value
                    elif key.endswith('_lte'):
                        cond = getattr(Model, key[: -len('_lte')]) <= value
                    elif key.endswith('_ne'):
                        cond = getattr(Model, key[: -len('_ne')]) != value
                    elif key.endswith('_like'):
                        cond = universal_re(
                            cast(getattr(Model, key[: -len('_like')]), String),
                            value,
                            query,
                        )
                    else:
                        cond = getattr(Model, key) == value
                    query = query.filter(cond)
                else:
                    col = getattr(Model, key)
                    query = query.filter(col.in_(values))

        # Search
        if params['q']:
            if hasattr(query, 'search'):
                query = query.search(params['q'])  # pragma: no cover
            else:
                query = query.filter(
                    or_(
                        *[
                            universal_re(
                                cast(getattr(Model, column), String),
                                params['q'],
                                query,
                            )
                            for column in self.rest.columns
                        ]
                    )
                )

        # Order
        if params['sort'] and request.method == 'GET':
            for sort, way in zip_longest(
                params['sort'].split(','),
                params['order'].split(','),
                fillvalue='asc',
            ):
                way = desc if way.lower() == 'desc' else asc

                if hasattr(Model, sort):
                    query = query.order_by(way(getattr(Model, sort)))
                else:
                    query = query.order_by(way(sort.split('.')[-1]))

        if request.method == 'GET':
            query = query.order_by(
                *[getattr(Model, pk) for pk in self.rest.primary_keys]
            )

        # Offset / Limit
        offset = int(params['start'] or 0)

        if params['page']:
            step = int(params['limit'] or 10)
            offset = max(int(params['page']) - 1, 0) * step

        elif params['end']:
            step = int(params['end']) - offset
        else:
            step = int(params['limit']) if params['limit'] else None

        if step:
            query = query.offset(offset).limit(step)

        return query
