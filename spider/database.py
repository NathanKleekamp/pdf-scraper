import os

from . import Base, engine
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref


def create_db():
    Base.metadata.create_all(engine)


class Link(Base):
    '''List of urls for the spider'''
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    pdf_id = Column(Integer, ForeignKey('pdfs.id'))
    pdf_url = relationship('Pdf', backref=backref('links', order_by=id))

    def __init__(self, url, visited=False):
        self.url = url
        self.visited = visited


class Pdf(Base):
    '''The pdf files themselves'''
    __tablename__ = 'pdfs'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)

    def __init__(self, url):
        self.url = url