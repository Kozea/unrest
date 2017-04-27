from datetime import timedelta

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Interval, Numeric, String

Base = declarative_base()


class Tree(Base):
    """Where money doesn't grow"""
    __tablename__ = 'tree'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    @property
    def fruit_colors(self):
        """The color of fruits"""
        return ', '.join([fruit.color for fruit in self.fruits])


class Fruit(Base):
    """A bag of fruit"""
    __tablename__ = 'fruit'
    fruit_id = Column('idf', Integer, primary_key=True)
    color = Column('hue', String(50))
    size = Column(Numeric)
    age = Column(Interval)
    tree_id = Column(Integer, ForeignKey('tree.id'))
    tree = relationship(Tree, backref='fruits')

    @hybrid_property
    def square_size(self):
        return self.size * self.size


def fill_data(session):
    pine = Tree(name='pine')
    maple = Tree(name='maple')
    oak = Tree(name='oak')
    session.add(pine)
    session.add(maple)
    session.add(oak)

    session.add(Fruit(
        color='grey', size=12,
        age=timedelta(days=12, hours=1, minutes=15),
        tree=pine))
    session.add(Fruit(
        color='darkgrey', size=23,
        age=timedelta(days=49, seconds=230, milliseconds=213),
        tree=pine))
    session.add(Fruit(
        color='brown', size=2.12,
        age=timedelta(0),
        tree=pine))
    session.add(Fruit(
        color='red', size=.5,
        age=timedelta(minutes=40),
        tree=maple))
    session.add(Fruit(
        color='orangered', size=100,
        age=timedelta(hours=2, microseconds=12),
        tree=maple))

    session.commit()
