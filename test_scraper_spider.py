#!/usr/bin/env python

import unittest

from cscraper import Spider, Url


class TestSpider(unittest.TestCase):
    def setUp(self):
        self.start = 'http://www.iana.org/domains/example/'
        self.spider = Spider(self.start)

    def tearDown(self):
        pass

    def test_parse_start(self):
        actual = self.spider.parse_start(self.start)
        expected = {base: 'http://www.iana.org',
                    directory: 'domains', path: 'domains/example/'}

    def test_get_links(self):
        actual = self.spider.get_site_links(self.start)
        expected = [
                 'http://www.iana.org/',
                 'http://www.iana.org/domains/',
                 'http://www.iana.org/numbers/',
                 'http://www.iana.org/protocols/',
                 'http://www.iana.org/about/',
                 'http://www.iana.org/go/rfc2606',
                 'http://www.iana.org/about/',
                 'http://www.iana.org/about/presentations/',
                 'http://www.iana.org/about/performance/',
                 'http://www.iana.org/reports/',
                 'http://www.iana.org/domains/',
                 'http://www.iana.org/domains/root/',
                 'http://www.iana.org/domains/int/',
                 'http://www.iana.org/domains/arpa/',
                 'http://www.iana.org/domains/idn-tables/',
                 'http://www.iana.org/protocols/',
                 'http://www.iana.org/numbers/',
                 'http://www.iana.org/abuse/',
                 'http://www.icann.org/',
                 'mailto:iana@iana.org?subject=General%20website%20feedback'
                 ]

    def get_pdfs(self):
        pass


if __name__ == '__main__':
    unittest.main()
