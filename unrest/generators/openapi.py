from datetime import timedelta
from decimal import Decimal


class OpenApi(object):
    __version__ = '3.0.0'

    def __init__(self, unrest):
        self.unrest = unrest

    def get_summaries_description(self, model_name):
        return {
            'GET': 'Retrieve all %s objects',
            'PUT': 'Replace all %s objects',
            'PATCH': 'Patch all %s objects',
            'POST': 'Add a new %s object',
            'DELETE': 'Delete all %s objects',
            'OPTIONS': 'Get info about the %s collection',
            'GET_one': 'Retrieve the corresponding %s object',
            'PUT_one': 'Replace the corresponding %s object or create it',
            'PATCH_one': 'Patch the corresponding %s object',
            'POST_one': 'Create a subcollection of %s object',
            'DELETE_one': 'Delete the corresponding %s object',
            'OPTIONS_one': 'Get info about the %s collection'
        }[model_name]

    def get_responses_description(self, model_name):
        return {
            'GET': 'All %s objects',
            'PUT': 'The new %s objects',
            'PATCH': 'The patched %s objects',
            'POST': 'The new %s object',
            'DELETE': 'All deleted %s objects',
            'OPTIONS': 'Info about the %s collection',
            'GET_one': 'The corresponding %s object',
            'PUT_one': 'The added %s object',
            'PATCH_one': 'The patched %s object',
            'POST_one': 'The subcollection %s object',
            'DELETE_one': 'The deleted %s object',
            'OPTIONS_one': 'Info about the %s collection'
        }[model_name]

    def get_requests_description(self, model_name):
        return {
            'PUT':
                'The new %s objects to replace the current collection with',
            'PATCH':
                'The %s objects patches',
            'POST':
                'The new %s object to create',
            'PUT_one':
                'The %s object to create or replace',
            'PATCH_one':
                'The %s object patches.'
        }[model_name]

    def get_info(self):
        info = {
            "title": self.unrest.app.name + ' unrest api',
            "version": self.unrest.version or '1.0'
        }
        info.update(**self.unrest.info)
        return info

    def get_servers(self):
        return [{
            'url': self.unrest.framework.url,
        }]

    def get_path_url(self, rest, params):
        path = rest.path
        if path.startswith(self.unrest.root_path):
            path = path[len(self.unrest.root_path):]
        if params:
            path += '/' + '/'.join('{%s}' % pk for pk in rest.primary_keys)
        return path

    def get_property(self, type):
        try:
            type = type.python_type
        except NotImplementedError:
            type = str
        # TODO bytea b64
        if issubclass(type, int):
            return {'type': 'integer', 'format': 'int64'}
        if issubclass(type, bool):
            return {'type': 'boolean'}
        if issubclass(type, (float, Decimal)):
            return {'type': 'number', 'format': 'double'}
        if issubclass(type, timedelta):
            return {'type': 'number'}
        return {'type': 'string'}

    def get_schema(self, rest, column_only=False):
        properties = {}
        properties.update({
            name: self.get_property(column.type)
            for name, column in rest.columns.items()
        })
        if not column_only:
            properties.update({
                property.name: self.get_property(property.sqlalchemy_type)
                for property in rest.properties
            })
        if not column_only:
            properties.update({
                name: {
                    "type": "array",
                    "items": self.get_schema(relationship)
                }
                for name, relationship in rest.relationships.items()
            })
        return {'type': 'object', 'properties': properties}

    def get_response_content(self, rest):
        return {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "primary_keys": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "occurences": {
                            "type": "integer"
                        },
                        "objects": {
                            "type": "array",
                            "items": self.get_schema(rest)
                        }
                    }
                }
            }
        }

    def get_operation_parameters(self, rest):
        return [{
            'name': pk,
            'in': 'path',
            'required': True,
            'schema': {
                'type': 'string'
            }
        } for pk in rest.primary_keys]

    def get_operation_request_body(self, rest, method, params):
        model = rest.Model.__name__
        method_key = method + ('_one' if params else '')
        schema = self.get_schema(rest, True)
        if not params and method != 'POST':
            schema = {
                "type": "object",
                "properties": {
                    "objects": {
                        "type": "array",
                        "items": schema
                    }
                }
            }
        return {
            'description': self.get_requests_description(method_key) % model,
            'content': {
                "application/json": {
                    "schema": schema
                }
            },
            'required': True
        }

    def get_operation(self, rest, params, method):
        model = rest.Model.__name__
        method_key = method + ('_one' if params else '')
        operation = {
            "tags": ['.'.join([v for v in (rest.table.schema, model) if v])],
            "summary": self.get_summaries_description(method_key) % model,
            "responses": {
                "200": {
                    "description":
                        self.get_responses_description(method_key) % model,
                    "content":
                        self.get_response_content(rest)
                }
            }
        }
        if params:
            operation['parameters'] = self.get_operation_parameters(rest)
        if method in ['PUT', 'PATCH', 'POST']:
            operation['requestBody'] = self.get_operation_request_body(
                rest, method, params
            )
        return operation

    def get_path(self, rest, params):
        methods = rest.methods
        if not params and not rest.allow_batch:
            methods = [
                m for m in methods if m not in ['PUT', 'DELETE', 'PATCH']
            ]
        if params:
            methods = [m for m in methods if m != 'POST']
        path = {
            method.lower(): self.get_operation(rest, params, method)
            for method in methods
        }
        if getattr(rest.Model, '__doc__', ''):
            path["summary"] = rest.Model.__doc__
        return path

    def get_paths(self):
        return {
            self.get_path_url(rest, params): self.get_path(rest, params)
            for rest in self.unrest.rests for params in (False, True)
        }

    def all(self):
        return {
            "openapi": self.__version__,
            "info": self.get_info(),
            "servers": self.get_servers(),
            "paths": self.get_paths()
        }
