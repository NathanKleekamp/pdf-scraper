#!/usr/bin/env python2.7

'''
Version 0.13
Spiders sections of J1 or Exchanges looking for pdfs and reports on
the PDF's location throughout the section.

By design, this script will not spider links offsite or the entirety
of those sites. Future versions may support spidering whole sites.
'''

import os
import re
import csv
import sys
import urlparse
import lxml
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
    '''Class that makes it simple to get a urls base and path quickly'''
    def __init__(self, url):
        self.url = url
        self.base = 'http://{0}'.format(urlparse.urlparse(url).netloc)
        self.path = urlparse.urlparse(url).path


# Setting globals
try:
    start = Url(sys.argv[1])
except IndexError:
    print('You must enter a starting point, like http://www.example.com/start/index.html')
    start = Url(raw_input('Enter a starting point: '))
if 'http://' not in start.url:
    start = Url(raw_input('The starting point must be a valid URL. Please enter a starting point: '))

try:
    html_flag = sys.argv[2].lower()
except IndexError:
    print("Your site's page links end in .html")
    html_flag = raw_input("Enter Yes or No: ").lower()
if html_flag not in ['yes', 'no']:
    html_flag = raw_input("Your site's page URLs end in .html? You must enter Yes or No: ")


def get_pdfs(soup, address):
    '''
    Grabs the pdfs on a page and saves them to the db if they're not already
    there. If it is already there, it records the page on which it's links.
    '''
    diff_pdfs = set([urlparse.urljoin(start.base, link.get('href')) for
                link in soup.find_all('a', href=re.compile('\.pdf'))])
    for pdf in diff_pdfs:
        if not session.query(Pdf).filter(
               Pdf.url==pdf).first():
            pdf = Pdf(pdf)
            pdf.page_urls.append(PageUrl(address))
            print('Adding PDF: {0}'.format(pdf.url))
            session.add(pdf)
        else:
            pdf = session.query(Pdf).filter(
                  Pdf.url==pdf).first()
            if address in [i.url for i in pdf.page_urls]:
                pass
            else:
                pdf.page_urls.append(PageUrl(address))
                session.add(pdf)
    session.commit()


def visited(address):
    '''Marks the pages as visited after being spidered'''
    not_visited = session.query(SpiderUrl).filter(
                  SpiderUrl.url==address).first
    if not_visited() is not None:
        url = not_visited()
        url.visited = True


def spider(soup, address):
    '''
    Grabs all the urls on a page then checks if they're in the section it's
    supposed to spider. If so, it looks at the db to see if it's already
    there. If it's not, it saves it to the db to be visited later. Once it's
    finished with the page, it marks it as visited.
    '''
    webpage_extensions = ['.html', '']
    get_pdfs(soup, address)
    # Looks for all <a href=""> links that don't start with # and prepends
    # the scheme and netloc to them.
    diff_links = set([urlparse.urljoin(start.base, link.get('href')) for
                      link in soup.find_all('a', href=re.compile(
                      r'^(?!#)'))])
    for link in diff_links:
        link = link.strip()
        if 'cms' in link or 'staging' in link:
            pass
        elif start.base not in link:
            pass
        elif os.path.splitext(link)[1] not in webpage_extensions:
            pass
        elif urlparse.urlparse(start.url).path.split('/')[1] in link:
            # Prevent the spider from entering redirect hell when the
            # the link doesn't end with / because it will never mark
            # /visited as /visited/ in the db
            if html_flag == 'no':
                if link[-1:] != '/':
                    link = link+'/'
            if not session.query(SpiderUrl).filter(
                   SpiderUrl.url==link).first():
                url = SpiderUrl(link)
                print('Adding {0} to db'.format(url.url))
                session.add(url)
    visited(address)
    session.commit()


def main():
    '''The function that makes it all happen.'''
    r = requests.get(start.url)
    while True:
        print('Checking {0}'.format(r.url))
        soup = BeautifulSoup(r.text, 'lxml')
        spider(soup, r.url)
        not_visited = session.query(SpiderUrl).filter(
                      SpiderUrl.visited==False).first
        if not not_visited():
            break
        r = requests.get(not_visited().url)
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
