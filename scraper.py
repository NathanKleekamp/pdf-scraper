#!/usr/bin/env python

'''
Spiders a site or section of a site looking for pdfs. By default, this
script will not spider links offsite.
'''

from __future__ import print_function

import re
import csv
import sys
import urlparse
import lxml
import domains
import requests

from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Boolean,\
     ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref


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


class Url(object):

    def __init__(self, url):
        self.url = url
        self.base = 'http://{0}'.format(urlparse.urlparse(url).netloc)
        self.path = urlparse.urlparse(url).path


try:
    start = Url(sys.argv[1])
except IndexError:
    print('You must enter a starting point, like http://exchanges.state.gov/heritage/index.html')
    start = Url(raw_input('Enter a starting point: '))


def get_pdfs(soup, address):
    unique_pdfs = set([link.get('href') for link in soup.find_all(
                      'a', href=re.compile('\.pdf'))])
    for pdf in unique_pdfs:
        if not session.query(Pdf).filter(
                Pdf.url==urlparse.urljoin(start.base, pdf)).first():
            pdf = Pdf(urlparse.urljoin(start.base, pdf))
            pdf.page_urls.append(PageUrl(address))
            session.add(pdf)
        else:
            pdf = session.query(Pdf).filter(
                  Pdf.url==urlparse.urljoin(start.base, pdf)).first()
            pdf.page_urls.append(PageUrl(address))
            session.add(pdf)
    session.commit()


def visited(soup, address):
    # This will not work on J1 because it's looking only for a path in the db
    # but if I store the complete url in db and get rid of .path, it should
    # work
    address = urlparse.urlparse(address).path
    not_visited = session.query(SpiderUrl).filter(
                  SpiderUrl.url==address).first
    if not_visited() is not None:
        url = not_visited()
        url.visited = True


def main():
    r = requests.get(start.url)
    while True:
        soup = BeautifulSoup(r.text, 'lxml')
        get_pdfs(soup, r.url)
        not_visited = session.query(SpiderUrl).filter(
                      SpiderUrl.visited==False).first
        if not not_visited():
            break
        r.requests.get(urlparse.urljoin(start.base, not_visited().url))
        if r.status_code == 404:
            pass
    with open('output.csv', 'wb') as f:
        writer = csv.writer(f)
        records = session.query(Pdf).join(PageUrl).all()
        for record in records:
            writer.writerow([record.url])
            for entry in record.page_urls:
                writer.writerow(['', entry.url])


if __name__ == '__main__':
    main()
