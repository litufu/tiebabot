from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()
engine = create_engine('sqlite:///tiebar.sqlite')


class Bar(Base):
    __tablename__ = 'bar'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Tie(Base):
    __tablename__ = 'tie'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    bar_id = Column(Integer, ForeignKey('bar.id'))
    bar = relationship(
        Bar,
        backref=backref('ties',
                        uselist=True,
                        cascade='delete,all'))


Base.metadata.create_all(engine)
