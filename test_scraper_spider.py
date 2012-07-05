#!/usr/bin/env python

import unittest

from cscraper import Spider


class TestSpider(unittest.TestCase):
    def setUp(self):
        with open('/Users/nathan/Desktop/example.html') as f:
                self.html = f.read()
        self.start = 'http://www.iana.org/domains/example/'
        self.spider = Spider(self.start)

    def tearDown(self):
        pass

    def test_parse_start(self):
        actual = self.spider.parse_start(self.start)
        expected = {'base': 'http://www.iana.org',
                    'directory': 'domains', 'path': 'domains/example/'}

    def test_get_links(self):
        actual = self.spider.get_links(self.html)
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

    def get_pdfs(self):
        actual = self.spider.get_pdfs(address)
        expected = set(['http://www.example.com/test/test.pdf'])


if __name__ == '__main__':
    unittest.main()
