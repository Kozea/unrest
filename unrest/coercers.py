import logging

log = logging.getLogger('unrest.coercers')


class Serialize(object):
    def __init__(self, model, columns):
        self.model = model
        self.columns = columns

    def dict(self):
        return {
            column.name: self.serialize(column)
            for column in self.columns
        }

    def serialize(self, column):
        return self._serialize(column.type, getattr(self.model, column.name))

    def _serialize(self, type, data):
        if data is None:
            return
        method_name = 'serialize_%s' % type.__class__.__name__.lower()

        if hasattr(self, method_name):
            return getattr(self, method_name)(type, data)

        log.debug('Missing method for type serialization %s' % method_name)

        return data

    def serialize_array(self, type, data):
        return [self._serialize(type.item_type, datum) for datum in data]

    def serialize_datetime(self, type, data):
        return data.isoformat()

    serialize_date = serialize_datetime
    serialize_time = serialize_datetime

    def serialize_interval(self, type, data):
        return data.total_seconds()

    def serialize_decimal(self, type, data):
        return float(data)
