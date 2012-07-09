import re
import logging
import urlparse
import lxml
import requests

from bs4 import BeautifulSoup
from . import Link, Pdf, Session

session = Session()

# Setting up logging
logging.basicConfig(filename='spider.log', filemode='w',
                    format='%(levelname)s: %(message)s',
                    level=logging.INFO)

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

    def save_pdf(self, pdf):
        pdf = Pdf(pdf)
        session.add(pdf)
        session.commit()

    def save_broken_links(self):
        pass

    def black_list(self):
        if self.blacklist:
            with open(self.blacklist) as f:
                return [line.strip() for line in f.readlines()]

    def crawl(self):
        while True:
            r = requests.get(self.start)
            soup = BeautifulSoup(r.text)
            links = self.get_links(soup)
            pdfs = self.get_pdfs(soup)
            break