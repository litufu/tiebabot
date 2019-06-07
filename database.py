from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func,Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()
engine = create_engine('sqlite:///tiebar.sqlite')


class Bar(Base):
    __tablename__ = 'bar'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    hassend = Column(Boolean)

class University(Base):
    __tablename__ = 'university'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    hassend = Column(Boolean)

# class GaoZhong(Base):
#     __tablename__ = 'gaozhong'
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     hassend = Column(Boolean)

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

class Search(Base):
    __tablename__ = 'search'
    id = Column(Integer, primary_key=True)
    tid = Column(String)
    has_reply = Column(Boolean)


Base.metadata.create_all(engine)
