#!/usr/bin/env python

'''
Scrapes exchanges for pdf files. Returns a csv file with each pdf in a given
section and the page(s) on which they're linked.
'''
from __future__ import print_function


import re
import csv
import sys
import lxml
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
    print('You must enter a starting point, like http://exchanges.state.gov/heritage/index.html')
    start = raw_input('Enter a starting point: ')

parsed = start.split('/')
baseurl = '/'.join(parsed[:3])
path = '/'.join(parsed[3:len(parsed)])
directory = parsed[3]
log = open('log.txt', 'a')


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
def visited(address):
    address = address.split(baseurl)[1]
    not_visited = session.query(SpiderUrl).filter(
                  SpiderUrl.url==address).first
    if not_visited() is not None:
        url = not_visited()
        url.visited = True


# This function will create duplicate copies on the page_urls table if the
# script is run on the same page more than once. Needs fixin'
def processor(soup, address):
    '''
    Spiders pages and looks for pdfs. Records on which page the pdf is
    located.
    '''
    spider_urls = soup.find_all('a', href=re.compile("\.html$"))
    unique_links = set([link.get('href') for link in spider_urls])
    pdf_links = soup.find_all('a', href=re.compile("\.pdf$"))
    unique_pdfs = set([link.get('href') for link in pdf_links])
    for link in unique_links:
        if 'cms' in link or 'staging' in link:
            message = 'Found link to CMS or staging ({0}) on: {1}\n'.format(
                       link, address)
            log.write(message)
            print(message, end='')
            pass
        elif directory in link and baseurl in link:
            message = 'Found non-relative link: {0} on: {1}\n'.format(
                        link, address)
            log.write(message)
            print(message, end='')
            pass
        # This should ignore outside links with directory name
        elif directory in link and 'http://' in link and basurl not in link:
            pass
        elif directory in link:
            if not session.query(SpiderUrl).filter(
                   SpiderUrl.url==link).all():
                message = 'Adding {0} to DB\n'.format(link)
                log.write(message)
                print(message, end='')
                url = SpiderUrl(link)
                session.add(url)
    for pdf in unique_pdfs:
        if not session.query(Pdf).filter(Pdf.url==pdf).first():
            pdf = Pdf(pdf)
            pdf.page_urls.append(PageUrl(address))
            session.add(pdf)
        else:
            pdf = session.query(Pdf).filter(
                  Pdf.url==pdf).first()
            pdf.page_urls.append(PageUrl(address))
            session.add(pdf)
    visited(address)
    session.commit()


def main():
    r = requests.get(start)
    while True:
        soup = BeautifulSoup(r.text, 'lxml')
        message = 'Checking {0}\n'.format(r.url)
        print(message, end='')
        log.write(message)
        processor(soup, r.url)
        not_visited = session.query(SpiderUrl).filter(
                        SpiderUrl.visited==False).first
        if not not_visited():
            break
        # This needs to be fixed. Should only check if not visited is a
        # relative url.
        r = requests.get(baseurl+not_visited().url)
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