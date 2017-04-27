import datetime
import decimal
import logging
from base64 import b64decode, b64encode

import dateutil
from sqlalchemy.types import String

log = logging.getLogger('unrest.coercers')


class Property(object):
    def __init__(self, name, sqlalchemy_type=None, formatter=None):
        self.name = name
        self.sqlalchemy_type = sqlalchemy_type or String()
        self.formatter = formatter

    def get(self, serializer, model):
        prop = getattr(model, self.name)
        if self.formatter:
            return self.formatter(prop)
        else:
            prop = serializer._serialize(self.sqlalchemy_type, prop)
        return prop


class Serialize(object):
    """
    Base serializer class

    Casts python sqlalchemy data into a JSON compliant type according to
    the sqlalchemy column type.

    Not all types are implemented as of now and it's fairly easy to add:
    Just add a `serialize_type` method for `type` and it shall work.

    The serialize class can be configured with the rest function and
    on the UnRest declaration.

    For example:
    ```python
    from unrest.coercers import Serialize

    class BetterSerialize(Serialize):
        def serialize_matrix(self, type, data):
            return data.matrix_to_string()

    rest = UnRest(app, session, SerializeClass=BetterSerialize)
    ...
    ```

    # Arguments
        model: The sqlachemy item to serialize.
        columns: The list of columns to serialize.
        properties: The list of properties to serialize.
        relationships: The list of relationships to serialize.
    """
    def __init__(self, model, columns, properties, relationships):
        self.model = model
        self.columns = columns
        self.properties = properties
        self.relationships = relationships

    def dict(self):
        """Serialize the given model to a JSON compatible dict"""
        if self.model is None:
            return {}

        def enforce_iterable(it):
            if it is None:
                return ()
            try:
                return iter(it)
            except TypeError:
                return (it,)

        return dict({
            name: self.serialize(name, column)
            for name, column in self.columns.items()
        }, **dict({
            property.name: property.get(self, self.model)
            for property in self.properties
        }, **{
            key: [
                relationship_rest.serialize_object(item)
                for item in enforce_iterable(getattr(self.model, key))
            ] for key, relationship_rest in self.relationships.items()
        }))

    def serialize(self, name, column):
        return self._serialize(column.type, getattr(self.model, name))

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
    serialize_numeric = serialize_decimal

    def serialize_largebinary(self, type, data):
        return b64encode(data).decode('utf-8')


class Deserialize(object):
    """
    Base deserializer class

    Casts JSON data back to compatible python sqlalchemy type.

    Not all types are implemented as of now and it's fairly easy to add:
    Just add a `deserialize_type` method for `type` and it shall work.

    The deserialize class can be configured with the rest function and
    on the UnRest declaration.

    For example:
    ```python
    from unrest.coercers import Deserialize

    class BetterDeserialize(Deserialize):
        def deserialize_matrix(self, type, data):
            return Matrix.from_string(data)

    rest = UnRest(app, session, DeserializeClass=BetterDeserialize)
    ...
    ```

    # Arguments
        payload: The JSON payload to deserialize
        columns: The list of columns to deserialize
    """
    def __init__(self, payload, columns):
        self.payload = payload
        self.columns = columns

    def merge(self, item, payload=None):
        """Deserialize the given payload into the existing sqlachemy `item`"""
        for name, column in self.columns.items():
            setattr(item, name, self.deserialize(name, column, payload))
        return item

    def create(self, factory):
        """
        Deserialize objects in the given payload into a list of new items
        created with the `factory` function.
        """
        return [
            self.merge(factory(), item) for item in self.payload['objects']]

    def deserialize(self, name, column, payload=None):
        payload = payload or self.payload
        if name not in payload:
            return None
        return self._deserialize(column.type, payload[name])

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

    def deserialize_integer(self, type, data):
        return int(data)

    def deserialize_decimal(self, type, data):
        return decimal.Decimal(data)
    deserialize_numeric = deserialize_decimal

    def deserialize_largebinary(self, type, data):
        return b64decode(data)
