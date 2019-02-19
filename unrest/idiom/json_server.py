import json
from collections import defaultdict
from itertools import zip_longest

from sqlalchemy import asc, desc, or_
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import String

from . import Idiom
from ..util import Response


class JsonServerIdiom(Idiom):
    PK_DELIM = '___'

    def request_to_data(self, request):
        if request.payload:
            try:
                return json.loads(request.payload.decode('utf-8'))

            except json.JSONDecodeError as e:
                self.rest.raise_error(400, 'JSON Error in payload: %s' % e)

    def data_to_response(self, data, request, status=200):
        if (
            request.method == 'GET'
            and self.rest.unrest.empty_get_as_404
            and 'occurences' in data
            and data['occurences'] == 0
        ):
            status = 404

        objects = data['objects']
        for object in objects:
            for key, relationship in self.rest.relationships.items():
                object[key] = [
                    self.PK_DELIM.join(
                        ref[pk] for pk in relationship.primary_keys
                    )
                    for ref in object[key]
                ]
        if request.parameters:
            objects = objects[0]
        payload = json.dumps(objects)
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
                        cond = cast(
                            getattr(Model, key[: -len('_like')]), String
                        ).op('~')(value)
                    else:
                        cond = getattr(Model, key) == value
                    query = query.filter(cond)
                else:
                    col = getattr(Model, key)
                    query = query.filter(col.in_(values))

        # Search
        if params['q']:
            if hasattr(query, 'search'):
                query = query.search(params['q'])
            else:
                query = query.filter(
                    or_(
                        *[
                            cast(getattr(Model, column), String).op('~')(
                                params['q']
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
        step = params['limit']
        if params['end']:
            step = int(params['end']) - offset
        else:
            step = int(params['limit']) if params['limit'] else None

        if step:
            query = query.offset(offset).limit(step)

        return query
