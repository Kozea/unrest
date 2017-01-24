import datetime
import decimal
import logging

import dateutil

log = logging.getLogger('unrest.coercers')


class Serialize(object):
    def __init__(self, model, columns):
        self.model = model
        self.columns = columns

    def dict(self):
        if self.model is None:
            return {}
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


class Deserialize(object):
    def __init__(self, payload, columns):
        self.payload = payload
        self.columns = columns

    def merge(self, item, payload=None):
        for column in self.columns:
            setattr(item, column.name, self.deserialize(column, payload))
        return item

    def create(self, factory):
        return [
            items.append(self.merge(factory(), item))
            for item in self.payload['objects']]

    def deserialize(self, column, payload=None):
        return self._deserialize(
            column.type, getattr(payload or self.payload, column.name))

    def _deserialize(self, type, data):
        if data is None:
            return
        method_name = 'deserialize_%s' % type.__class__.__name__.lower()

        if hasattr(self, method_name):
            return getattr(self, method_name)(type, data)

        log.debug('Missing method for type deserialization %s' % method_name)

        return data

    def deserialize_datetime(self, type, data):
        return dateutil.parser.parse(data)

    def deserialize_date(self, type, data):
        return dateutil.parser.parse(data).date()

    def deserialize_time(self, type, data):
        return dateutil.parser.parse(data).time()

    def deserialize_interval(self, type, data):
        return datetime.timedelta(seconds=data)

    def deserialize_decimal(self, type, data):
        return decimal.Decimal(data)
