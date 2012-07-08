#!/usr/bin/env python

# sys path hack
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

import unittest

from bs4 import BeautifulSoup

from spider import Spider, Pdf, Link, session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestSpider(unittest.TestCase):
    """Test case for the Spider clas"""
    def setUp(self):
        """Set up"""
        with open(os.path.abspath(('/Users/nathankleekamp/Python/spider/'
                                   'example.html'))) as f:
            self.html = f.read()
        self.start = 'http://www.iana.org/domains/example/'
        self.spider = Spider(self.start,
                      blacklist=('/Users/nathankleekamp/Python/'
                                 'spider/blacklist.txt'))
        self.soup = BeautifulSoup(self.html)

    def tearDown(self):
        """Tear down"""
        pass

    def test_get_links(self):
        """Tests only links are being collected"""
        actual = self.spider.get_links(self.soup)
        expected = set([
            'http://www.example.com/test/test.pdf',
            'http://www.icann.org/',
            'https://www.iana.org/',
            'https://www.iana.org/about/',
            'https://www.iana.org/about/performance/',
            'https://www.iana.org/about/presentations/',
            'https://www.iana.org/abuse/',
            'https://www.iana.org/domains/',
            'https://www.iana.org/domains/arpa/',
            'https://www.iana.org/domains/idn-tables/',
            'https://www.iana.org/domains/int/',
            'https://www.iana.org/domains/root/',
            'https://www.iana.org/go/rfc2606',
            'https://www.iana.org/numbers/',
            'https://www.iana.org/protocols/',
            'https://www.iana.org/reports/',
            'https://www.iana.org/nathan/test/'
             ])
        self.assertEqual(actual, expected)

    def test_get_pdfs(self):
        """Tests that pdfs are being found on page"""
        actual = self.spider.get_pdfs(self.soup)
        expected = set(['http://www.example.com/test/test.pdf'])
        self.assertEqual(actual, expected)

    def test_save_pdfs(self):
        """Tests that pdfs are being saved to db"""
        pass

    def test_save_broken_links(self):
        """Tests broken links are saved to db"""
        pass

    def test_black_list(self):
        """Tests black list is being pulled in"""
        actual = self.spider.black_list()
        expected = ['http://exchanges.state.gov/heritage/iraq.html',
                    'http://exchanges.state.gov/heritage/special.html']
        self.assertEqual(actual, expected)

    def test_crawl(self):
        """Tests the workhorse"""
        actual = self.spider.crawl()


if __name__ == '__main__':
    unittest.main()
