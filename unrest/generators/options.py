class Options(object):
    def __init__(self, unrest):
        self.unrest = unrest

    def get_property(self, type):
        try:
            return type.python_type.__name__
        except NotImplementedError:
            return type.__class__.__name__

    def get_columns(self, rest):
        return {
            name: self.get_property(column.type)
            for name, column in rest.columns.items()
        }

    def get_properties(self, rest):
        return {
            property.name: self.get_property(property.sqlalchemy_type)
            for property in rest.properties
        }

    def get_relationships(self, rest):
        return {
            name: {
                k: v
                for k, v in self.get_route(relationship).items()
                if k != 'methods'
            }
            for name, relationship in rest.relationships.items()
        }

    def get_route(self, rest):
        return {
            'model': rest.Model.__name__,
            'description': getattr(rest.Model, '__doc__', ''),
            'parameters': list(rest.primary_keys),
            'columns': self.get_columns(rest),
            'properties': self.get_properties(rest),
            'relationships': self.get_relationships(rest),
            'methods': rest.methods,
            'batch': rest.allow_batch
        }

    def all(self):
        return {rest.path: self.get_route(rest) for rest in self.unrest.rests}
