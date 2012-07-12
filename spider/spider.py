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
            soup = BeautifulSoup(r.text, 'lxml')
            self.spider_q.put(soup)
            logging.info('Getting: {0}'.format(soup.title.contents[0]))
            print('Getting: {0}'.format(soup.title.contents[0]))
            self.url_q.task_done()


class DataWrite(Thread):
    def __init__(self, db_q, page):
        Thread.__init__(self)
        self.db_q = db_q
        self.page = page

    def run(self):
        while True:
            pdf = self.db_q.get()
            if not session.query(Pdf).filter(Pdf.url==pdf).first():
                pdf = Pdf(pdf)
                pdf.links.append(Link(self.page))
                logging.info('Adding {0}'.format(pdf))
                print('Adding {0}'.format(pdf))
                session.add(pdf)
            else:
                pdf = session.query(Pdf).filter(Pdf.url==pdf).first()
                if self.page in [i.url for i in pdf.links]:
                    pass
                else:
                    pdf.links.append(Link(self.page))
                    logging.info('Adding {0} to {1}'.format(self.page, pdf))
                    session.add(pdf)
            self.db_q.task_done()


class Spider(Thread):
    def __init__(self, start, depth=0, follow=False, blacklist=None):
        self.start = start
        self.depth = depth
        self.follow = follow
        self.blacklist = blacklist
        self.parsed = urlparse.urlparse(self.start)
        self.soup = BeautifulSoup(requests.get(self.start).text, 'lxml')
        self.url_q = url_q
        self.spider_q = spider_q
        self.db_q = db_q

    #def run(self):
        #while True
        #    soup = self.spider_q.get()


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

    def save_broken_links(self):
        pass

    def black_list(self):
        if self.blacklist:
            with open(self.blacklist) as f:
                return [line.strip() for line in f.readlines()]

    def crawl(self):
        pass