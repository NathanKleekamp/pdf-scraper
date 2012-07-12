# sys.path hack
import os
import sys
sys.path.insert(0, os.path.abspath('../'))

import unittest
import requests

from Queue import Queue
from bs4 import BeautifulSoup

from spider import Spider, Pdf, Link, GrabSoup, DataWrite, Session

session = Session()

class TestSpider(unittest.TestCase):
    """Test case for the Spider clas"""
    def setUp(self):
        """Set up"""
        self.spider_q = Queue()
        self.db_q = Queue()
        self.url_q = Queue()
        for i in range(5):
            self.spider = Spider(self.spider_q, self.db_q, self.url_q,
                          self.start, blacklist=(os.path.abspath(
                          'blacklist.txt')))
            self.spider.setDaemon(True)
            self.spider.start()
        self.pages = ['http://exchanges.state.gov/heritage/index.html',
                      'http://exchanges.state.gov/heritage/iraq.html',
                      'http://exchanges.state.gov/heritage/special.html',
                      'http://exchanges.state.gov/heritage/culprop.html',
                      'http://exchanges.state.gov/heritage/afcp.html']
        self.start = pages[0]
        self.soups = [BeautifulSoup(requests.get(page).text) for page in
                      self.pages]
        for soup in self.soups:
            self.spider_q.get(soup)
        self.spider_q.join()
        self.soup = soups[0]

    def test_get_links(self):
        """Tests only links to web pages are being collected"""
        actual = self.spider.get_links(self.soup)
        expected = set([
            'http://exchanges.state.gov/scho-pro.html',
            'http://www.state.gov/misc/87529.htm#privacy',
            'http://www.state.gov/m/a/ips/',
            'http://exchanges.state.gov/alumni/index.html',
            'http://exchanges.state.gov/student.html',
            'http://exchanges.state.gov/programs/professionals.html',
            'http://exchanges.state.gov/about/assistant-secretary-stock.html',
            'http://exchanges.state.gov/news/index.html',
            'http://exchanges.state.gov/heritage/index.html',
            'http://exchanges.state.gov/heritage/1sindex.html',
            'http://exchanges.state.gov/heritage/culprop.html',
            'http://exchanges.state.gov/mobile/index.html',
            'http://j1visa.state.gov/',
            'http://www.state.gov/misc/415.htm',
            'http://exchanges.state.gov/index.html',
            'http://exchanges.state.gov/sports/index.html',
            'http://exchanges.state.gov/grants/preparing_payment.html',
            'http://state.gov/',
            'http://exchanges.state.gov/grants/faqs.html',
            'http://exchanges.state.gov/heritage/whatsnew.html',
            'http://exchanges.state.gov/',
            'http://exchanges.state.gov/about/program_offices.html',
            'http://exchanges.state.gov/englishteaching/forum-journal.html',
            'http://www.state.gov/misc/60289.htm',
            'http://exchanges.state.gov/heritage/iraq.html',
            'http://exchanges.state.gov/grants/terminology.html',
            'http://exchanges.state.gov/heritage/sindex.html',
            'http://exchanges.state.gov/heritage/special.html',
            'http://exchanges.state.gov/grants/preparing_reports.html',
            'http://exchanges.state.gov/programevaluations/index.html',
            'http://exchanges.state.gov/programs/scholars.html',
            'http://exchanges.state.gov/programs/cultural.html',
            'http://exchanges.state.gov/programs/secondary-school.html',
            'http://www.usa.gov/',
            'http://exchanges.state.gov/about/contact-us.html',
            'http://exchanges.state.gov/programs/university.html',
            'http://www.state.gov/misc/87529.htm#copyright',
            'http://exchanges.state.gov/grants/open2.html',
            'http://exchanges.state.gov/programs/english-language.html',
            'http://exchanges.state.gov/jexchanges/ppp.html',
            'http://exchanges.state.gov/pro-admin.html',
            'http://exchanges.state.gov/search.html',
            'http://exchanges.state.gov/grants/cfda.html',
            'http://www.iawg.gov/',
            'http://exchanges.state.gov/englishteaching/resources-et.html',
            ('http://exchanges.state.gov/heritage/culprop/index/'
                                        'pdfs/unesco01.pdf'),
            'http://exchanges.state.gov/heritage/afcp.html',
            'http://exchanges.state.gov/features/index.html',
            'http://exchanges.state.gov/host/index.html',
            'http://exchanges.state.gov/about/employment.html',
            'http://exchanges.state.gov/programs/educators.html',
            'http://exchanges.state.gov/a-z.html',
            'http://exchanges.state.gov/about.html',
            ('http://exchanges.state.gov/programevaluations/'
                                        'program-evaluations.html'),
             ])
        self.assertEqual(actual, expected)

    def test_get_pdfs(self):
        """Tests that pdfs are being found on page"""
        actual = self.spider.get_pdfs(self.soup)
        expected = set([('http://exchanges.state.gov/heritage/culprop/index/'
                                                     'pdfs/unesco01.pdf')])
        self.assertEqual(actual, expected)

    def test_black_list(self):
        """Tests black list is being pulled in"""
        actual = self.spider.black_list()
        expected = ['http://exchanges.state.gov/heritage/iraq.html',
                    'http://exchanges.state.gov/heritage/special.html']
        self.assertEqual(actual, expected)

    def test_threaded_processing_pdfs(self):
        actual = []

    def tearDown(self):
        """Tear down"""
        pass


class TestGrabSoup(unittest.TestCase):
    def setUp(self):
        '''Sets up tests'''
        self.pages = ['http://exchanges.state.gov/heritage/index.html',
                      'http://exchanges.state.gov/heritage/culprop.html',
                      'http://exchanges.state.gov/heritage/special.html']
        self.url_q = Queue()
        self.spider_q = Queue()
        for i in range(3):
            gs = GrabSoup(self.url_q, self.spider_q)
            gs.setDaemon(True)
            gs.start()

    def test_grab_soup(self):
        for page in self.pages:
            self.url_q.put(page)
        self.url_q.join()
        actual = [i.title.contents[0] for i in self.spider_q.queue]
        expected = [u'Cultural Heritage Center',
                    u'International Cultural Property Protection',
                    u'Special Projects']
        for i in expected:
            self.assertTrue(i in actual)

    def tearDown(self):
        '''Removes everything after tests'''
        pass


class TestDataWrite(unittest.TestCase):
    def setUp(self):
        '''Sets up tests'''
        self.pdfs = ['test1.pdf', 'test2.pdf']
        self.page = 'http://exchanges.state.gov/heritage/index.html'
        self.db_q = Queue()
        for i in range(2):
            dw = DataWrite(self.db_q, self.page)
            dw.setDaemon(True)
            dw.start()

    def test_a_threaded_write(self):
        "Tests writes in threads"
        for pdf in self.pdfs:
            self.db_q.put(pdf)
        self.db_q.join()
        session.commit()
        actual = [i.url for i in session.query(Pdf).all()]
        expected = ['test1.pdf', 'test2.pdf']
        for i in expected:
            self.assertTrue(i in actual)

# I dont' think this is a legitimate test of the functionality
    def test_b_link_append(self):
        "Tests that links are successfully appended to pdfs"
        actual = {}
        test2 = session.query(Pdf).filter(Pdf.url=='test2.pdf').first()
        test2.links.append(Link(
                            u'http://exchanges.state.gov/heritage/iraq.html'))
        pdfs = session.query(Pdf).join(Link).all()
        for pdf in pdfs:
            actual[pdf.url] = [i.url for i in pdf.links]
        expected = {
            u'test1.pdf': [u'http://exchanges.state.gov/heritage/index.html'],
            u'test2.pdf': [u'http://exchanges.state.gov/heritage/index.html',
                          u'http://exchanges.state.gov/heritage/iraq.html']
            }
        self.assertEqual(actual, expected)

    def tearDown(self):
        session.close()

if __name__ == '__main__':
    unittest.main()