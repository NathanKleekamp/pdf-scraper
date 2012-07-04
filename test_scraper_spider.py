#!/usr/bin/env python

import unittest

from cscraper import Spider


class TestSpider(unittest.TestCase):
    def setUp(self):
        self.start = 'http://exchanges.state.gov/heritage/index.html'
        self.spider = Spider(self.start)

    def tearDown(self):
        pass

    def test_get_links(self):
        self.spider.get_links()


if __name__ == '__main__':
    unittest.main()
