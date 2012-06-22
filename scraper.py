#!/usr/bin/env python

'''
Scrapes exchanges for pdf files. Returns a csv file with each pdf in a given
section and the page(s) on which they're linked.
'''


import re
import sys
import requests

from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Boolean,\
     ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref


# Global Variables
try:
    start = sys.argv[1]
except IndexError:
    print('You must enter a starting point, like heritage/index.html')
    start = raw_input('Enter a starting point: ')

if start[0] == '/':
    start = start[1:]

_baseurl = 'http://exchanges.state.gov/'
full_url = _baseurl+start
directory = start.split('/')


# Setting up the database and database classes
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class SpiderUrl(Base):
    '''List of urls for the spider'''
    __tablename__ = 'urls'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    visited = Column(Boolean, default=False)

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


class PageUrl(Base):
    '''Pages on which the pdf is linked'''
    __tablename__ = 'page_urls'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    pdf_id = Column(Integer, ForeignKey('pdfs.id'))
    pdf_url = relationship('Pdf', backref=backref('page_urls', order_by=id))

    def __init__(self, url):
        self.url = url


Base.metadata.create_all(engine)


# Functions
def get_pdfs(soup, address=None):
    '''
    Obtains a list of pdfs on a given page and saves pdf linke to the db.
    '''
    pdf_links = soup.find_all('a', href=re.compile("\.pdf$"))
    unique_pdfs = set([link.get('href') for link in pdf_links])
    for pdf in unique_pdfs:
        if not session.query(Pdf).filter(Pdf.url==pdf).all():
            pdf = Pdf(pdf)
            pdf.page_urls.append(PageUrl(address))
            session.add(pdf)
        else:
            pdf = session.query(Pdf).filter(
                  Pdf.url==pdf).all()
            pdf[0].page_urls.append(PageUrl(address))
            session.add(pdf[0])
    session.commit()


def get_urls(soup):
    '''Grabs urls to pages within the same "directory/folder"'''
    spider_urls = soup.find_all('a', href=re.compile("\.html$"))
    unique_links = set([link.get('href') for link in spider_urls])
    for link in unique_links:
        print('Checking {0}'.format(link))
        if directory[0] in link:
            if not session.query(SpiderUrl).filter(
                   SpiderUrl.url==link).all():
                print('Adding {0} to DB'.format(link))
                url = SpiderUrl(link)
                session.add(url)
    session.commit()


# May not need a generator function
def not_visited():
    yield not_visited


def main():
    '''The work horse'''
    r = requests.get(full_url)
    soup = BeautifulSoup(r.text)
    get_pdfs(soup, address=r.url)
    get_urls(soup)
    not_visited = session.query(SpiderUrl).filter(
                  SpiderUrl.visited==False).first()
    #visited = session.query(SpiderUrl).filter(SpiderUrl.url==r.text).all
    #for i in visited:
    #    i.visited = True
    #full_url = not_visited()


if __name__ == '__main__':
    main()
