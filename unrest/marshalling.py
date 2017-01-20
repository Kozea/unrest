import logging
from sqlalchemy.types import (
    Date, DATE, DateTime, DATETIME, Time, TIME, DECIMAL, Numeric, NUMERIC)

log = logging.getLogger('unrest.marshalling')


def marshall_date(data):
    return data.isoformat()


def marshall_datetime(data):
    return data.isoformat()


def marshall_time(data):
    return data.isoformat()


def marshall_time(data):
    return data.isoformat()


def marshall_decimal(data):
    return float(data)


# SqlAlchemy types that do not convert to json
CONVERTERS = {
    Date: marshall_date,
    DATE: marshall_date,
    DateTime: marshall_datetime,
    DATETIME: marshall_datetime,
    Time: marshall_time,
    TIME: marshall_time,
    DECIMAL: marshall_decimal,
    Numeric: marshall_decimal,
    NUMERIC: marshall_decimal,
}


def marshall(model, column):
    data = getattr(model, column.name)
    if data is not None and column.type.__class__ in CONVERTERS:
        return CONVERTERS[column.type.__class__](data)
    return data
