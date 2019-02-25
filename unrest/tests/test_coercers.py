from datetime import date, datetime, time, timedelta

from sqlalchemy import types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column

from ..coercers import Deserialize, Serialize

Base = declarative_base()


class Item(Base):
    __tablename__ = 'item'
    id = Column(types.Integer, primary_key=True)
    str = Column(types.String)
    date = Column(types.Date)
    time = Column(types.Time)
    datetime = Column(types.DateTime)
    data = Column(types.LargeBinary)
    boolean = Column(types.Boolean)
    array = Column(types.ARRAY(types.Interval))


def test_serialize():
    item = Item(
        str='str',
        date=date(2020, 12, 21),
        time=time(12, 1, 21),
        datetime=datetime(2050, 3, 26, 17, 40, 14),
        data=b'BIG DATA',
        boolean=True,
        array=[
            timedelta(days=4),
            timedelta(weeks=2),
            timedelta(seconds=48),
            timedelta(hours=21),
        ],
    )
    serialize = Serialize(
        item,
        {
            'str': Item.str,
            'date': Item.date,
            'time': Item.time,
            'datetime': Item.datetime,
            'data': Item.data,
            'boolean': Item.boolean,
            'array': Item.array,
        },
        [],
        {},
    )
    assert serialize.dict() == {
        'date': '2020-12-21',
        'datetime': '2050-03-26T17:40:14',
        'str': 'str',
        'time': '12:01:21',
        'data': 'QklHIERBVEE=',
        'boolean': True,
        'array': [345_600.0, 1_209_600.0, 48.0, 75600.0],
    }


def test_deserialize():
    item = Item()
    deserialize = Deserialize(
        {
            'date': '2020-12-21',
            'datetime': '2050-03-26T17:40:14',
            'str': 'str',
            'time': '12:01:21',
            'data': 'QklHIERBVEE=',
            'boolean': True,
            'array': [345_600.0, 1_209_600.0, 48.0, 75600.0],
        },
        {
            'str': Item.str,
            'date': Item.date,
            'time': Item.time,
            'datetime': Item.datetime,
            'data': Item.data,
            'boolean': Item.boolean,
            'array': Item.array,
        },
    )
    deserialize.merge(item)
    assert item.str == 'str'
    assert item.date == date(2020, 12, 21)
    assert item.time == time(12, 1, 21)
    assert item.datetime == datetime(2050, 3, 26, 17, 40, 14)
    assert item.data == b'BIG DATA'
    assert item.boolean is True
    assert item.array == [
        timedelta(days=4),
        timedelta(weeks=2),
        timedelta(seconds=48),
        timedelta(hours=21),
    ]
