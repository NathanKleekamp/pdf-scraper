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
start = start.split('/')


# Setting up the database and database classes
engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Url(Base):
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
    pdf_url = Column(String, unique=True)

    def __init__(self, pdf_url):
        self.pdf_url = pdf_url


class PdfUrl(Base):
    '''Pages on which the pdf is found'''
    __tablename__ = 'pdf_pages'
    id = Column(Integer, primary_key=True)
    page_url = Column(String)
    pdf_id = Column(Integer, ForeignKey('pdfs.id'))
    pdf_address = relationship('Pdf', backref=backref('pdf_pages', order_by=id))

    def __init__(self, page_url):
        self.page_url = page_url


Base.metadata.create_all(engine)


# Functions
def get_pdfs(soup, address=None):
    '''Obtains a list of pdfs on a given page and saves them to the db.'''
    pdf_links = soup.find_all('a', href=re.compile("\.pdf$"))
    unique_pdfs = set([link.get('href') for link in pdf_links])
    # Need to check if pdf already in the database before next step
    for pdf in unique_pdfs:
        pdf = Pdf(pdf)
        pdf.pdf_pages = [PdfUrl(address)]
        session.add(pdf)
    session.commit()


def get_urls(soup):
    '''Grabs urls to pages within the same "directory/folder"'''
    spider_urls = soup.find_all('a', href=re.compile("\.html$"))
    unique_links = set([link.get('href') for link in spider_urls])
    # Not fully tested
    for link in unique_links:
        if start[0] in link:
            url = Url(link)
            session.add(url)
    session.commit()


def main():
    '''The work horse'''
    r = requests.get(full_url)
    soup = BeautifulSoup(r.text)
    get_pdfs(soup, address=r.url)
    get_urls(soup)


if __name__ == '__main__':
    main()
