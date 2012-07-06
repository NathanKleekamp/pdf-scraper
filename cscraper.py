#!/usr/bin/env python2.7

'''
Version 0.2
Spiders sections of J1 or Exchanges looking for pdfs and reports on
the PDF's location throughout the section.

By design, this script will not spider links offsite or the entirety
of those sites. Future versions may support spidering whole sites.
'''

import os
import re
import csv
import sys
import pprint
import logging
import urlparse
import lxml
import requests

from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Boolean, \
     ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref


# Setting up logging
logging.basicConfig(filename='spider.log', filemode='w',
                    format='%(levelname)s: %(message)s',
                    level=logging.INFO)


# Setting up the database and database classes
Session = sessionmaker()
engine = create_engine('sqlite:///database.db')
Session.configure(bind=engine)
session = Session()
Base = declarative_base()


class Link(Base):
    '''List of urls for the spider'''
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    visited = Column(Boolean, default=False)
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


Base.metadata.create_all(engine)


class Spider(object):
    def __init__(self, start, depth=0, follow=False, blacklist=None):
        self.start = start
        self.depth = depth
        self.follow = follow
        self.blacklist = blacklist
        self.parsed = urlparse.urlparse(self.start)

    def get_links(self, soup):
        # Normalizes relative and absolute urls when grabbing urls on page
        return set([urlparse.urljoin(self.start, link.get('href')) 
                    for link in soup.find_all('a', href=re.compile(
                    r'^(?![(#)(mailto)(javascript)])'))])

    def get_pdfs(self, soup):
        # Normalizes relative and absolute urls when grabbing pdfs on page
        return set([urlparse.urljoin(self.start, link.get('href'))
                    for link in soup.find_all('a', href=re.compile(
                    '\.pdf'))])

    def save_pdfs(self):
        pass

    def save_broken_links(self):
        pass

    def black_list(self):
        with open(self.blacklist) as f:
            return [line.strip() for line in f.readlines()]

    def crawl(self):
        while True:
            r = requests.get(self.start)
            soup = BeautifulSoup(r.text)
            links = self.get_links(soup)
            pprint.pprint(links)
            pdfs = self.get_pdfs(soup)
            pprint.pprint(pdfs)
            break


def main():
    spider = Spider(start)
    spider.crawl()

if __name__ == '__main__':
    start = 'http://exchanges.state.gov/heritage/index.html'
    main()
