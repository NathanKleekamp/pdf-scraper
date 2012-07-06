#!/usr/bin/env python

import unittest

from bs4 import BeautifulSoup

from cscraper import Spider


class TestSpider(unittest.TestCase):
    def setUp(self):
        with open('example.html') as f:
                self.html = f.read()
        self.start = 'http://www.iana.org/domains/example/'
        self.spider = Spider(self.start, blacklist='blacklist.txt')
        self.soup = BeautifulSoup(self.html)

    def tearDown(self):
        pass

    def test_get_links(self):
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
            'https://www.iana.org/reports/'
             ])
        self.assertEqual(actual, expected)

    def test_get_pdfs(self):
        actual = self.spider.get_pdfs(self.soup)
        expected = set(['http://www.example.com/test/test.pdf'])
        self.assertEqual(actual, expected)

    def test_save_pdfs(self):
        pass

    def test_broken_links(self):
        pass

    def test_black_list(self):
        actual = self.spider.black_list()
        expected = ['http://exchanges.state.gov/heritage/iraq.html',
                    'http://exchanges.state.gov/heritage/special.html']
        self.assertEqual(actual, expected)

    def test_crawl(self):
        actual = self.spider.crawl()
        expected = []


if __name__ == '__main__':
    unittest.main()
