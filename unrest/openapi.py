summaries = {
    'GET': 'Retrieve all %s objects',
    'PUT': 'Replace all %s objects',
    'PATCH': 'Patch all %s objects',
    'POST': 'Add a new %s object',
    'DELETE': 'Delete all %s objects',
    'OPTIONS': 'Get info about the %s collection',
    'GET_with_pk': 'Retrieve the corresponding %s object',
    'PUT_with_pk': 'Replace the corresponding %s object or create it',
    'PATCH_with_pk': 'Patch the corresponding %s object',
    'POST_with_pk': 'Create a subcollection of %s object',
    'DELETE_with_pk': 'Delete the corresponding %s object',
    'OPTIONS_with_pk': 'Get info about the %s collection'
}
responses = {
    'GET': 'All %s objects',
    'PUT': 'The new %s objects',
    'PATCH': 'The patched %s objects',
    'POST': 'The new %s object',
    'DELETE': 'All deleted %s objects',
    'OPTIONS': 'Info about the %s collection',
    'GET_with_pk': 'The corresponding %s object',
    'PUT_with_pk': 'The added %s object',
    'PATCH_with_pk': 'The patched %s object',
    'POST_with_pk': 'The subcollection %s object',
    'DELETE_with_pk': 'The deleted %s object',
    'OPTIONS_with_pk': 'Info about the %s collection'
}
requests = {
    'PUT': 'The new %s objects to replace the current collection with',
    'PATCH': 'The %s objects patches',
    'POST': 'The new %s object to create',
    'PUT_with_pk': 'The %s object to create or replace',
    'PATCH_with_pk': 'The %s object patches.'
}


def response_content(model):
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
                        "items": {
                            "$ref": "#/components/schemas/" + model
                        }
                    },
                },
            }
        }
    }


def columns_to_schema(columns):
    return {
        'type': 'object',
        'properties': {
            name: {
                'type': {
                    'int': 'integer',
                    'bool': 'boolean',
                    'float': 'number',
                    'timedelta': 'number',
                    'Decimal': 'number'
                }.get(type, 'string'),
                'format': {
                    'datetime': 'date-time',
                    'int': 'int64',
                    'Decimal': 'double',
                    'string': '',
                    'boolean': '',
                }.get(type, type)
            }
            for name, type in columns.items()
        }
    }


def openapi(infos, url, root_path, info, name, version):
    paths = {}
    components = {'schemas': {}}
    for path, infos in infos.items():
        model = infos['model']
        for withPk in (False, True):
            if path.startswith(root_path):
                path = path[len(root_path):]
            if withPk:
                path = path + '/' + '/'.join(
                    '{%s}' % param for param in infos['parameters']
                )
            paths[path] = {'summary': infos['description']}
            components['schemas'][model] = columns_to_schema(infos['columns'])
            for method in infos['methods']:
                if not withPk and not infos['batch'] and method in [
                        'PUT', 'DELETE', 'PATCH'
                ] or withPk and method == 'POST':
                    continue
                method_key = method + ('_with_pk' if withPk else '')
                paths[path][method.lower()] = {
                    "tags": [' -> '.join([
                        v for v in (infos['schema'], model) if v])],
                    "summary": summaries[method_key] % model,
                    "responses": {
                        "200": {
                            "description": responses[method_key] % model,
                            "content": response_content(model)
                        }
                    }
                }
                if withPk:
                    paths[path][method.lower()]['parameters'] = [{
                        'name': pk,
                        'in': 'path',
                        'required': True
                    } for pk in infos['parameters']]
                if method in ['PUT', 'PATCH', 'POST']:
                    paths[path][method.lower()]['requestBody'] = {
                        'description': requests[method_key] % model,
                        'content': {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/" + model
                                } if withPk or method == 'POST' else {
                                    "type": "object",
                                    "properties": {
                                        "objects": {
                                            "type": "array",
                                            "items": {
                                                "$ref":
                                                    "#/components/schemas/" +
                                                    model
                                            }
                                        },
                                    },
                                }
                            }
                        },
                        'required': True
                    }

    info = {"title": name + ' unrest api', "version": version or '1.0'}
    info.update(**info)

    return {
        "openapi": "3.0.0",
        "info": info,
        "servers": [{
            'url': url
        }],
        "paths": paths,
        "components": components
    }
