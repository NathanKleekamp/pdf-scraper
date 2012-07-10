import re
import logging
import urlparse

import lxml
import requests

from Queue import Queue
from threading import Thread

from bs4 import BeautifulSoup

from . import Link, Pdf, Session

session = Session()
url_q = Queue()
spider_q = Queue()
db_q = Queue()

# Setting up logging
logging.basicConfig(filename='spider.log', filemode='w',
                    format='%(levelname)s: %(message)s',
                    level=logging.INFO)


# How do I get the spider_q back to the Spider class
class GrabSoup(Thread):
    '''This class grabs the soup'''
    def __init__(self, url_q, spider_q):
        Thread.__init__(self)
        self.url_q = url_q
        self.spider_q = spider_q

    def run(self):
        while True:
            page = self.url_q.get()
            r = requests.get(page)
            soup = BeautifulSoup(r.text)
            self.spider_q.put(soup)
            self.url_q.task_done()


class DataWrite(Thread):
    def __init__(self, db_q):
        Thread.__init__(self)
        self.db_q = db_q

    def run(self):
        pass


class Spider(object):
    def __init__(self, start, depth=0, follow=False, blacklist=None):
        self.start = start
        self.depth = depth
        self.follow = follow
        self.blacklist = blacklist
        self.parsed = urlparse.urlparse(self.start)
        self.soup = BeautifulSoup(requests.get(self.start).text, 'lxml')

    def get_links(self, soup):
        # Normalizes relative and absolute urls when grabbing urls on page
        return set([urlparse.urljoin(self.start, link.get('href'))
                    for link in soup.find_all('a', href=re.compile(
                    r'^(?![(#)(mailto)(javascript)])'))])

    def get_pdfs(self, soup):
        pdfs = set()
        for link in self.get_links(soup):
            if re.search('\.pdf', link):
                pdfs.add(link)
        return pdfs

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
        r = requests.get(self.start)
        while True:
            soup = BeautifulSoup(r.text)
            links = self.get_links(soup)
            pdfs = self.get_pdfs(soup)
            break