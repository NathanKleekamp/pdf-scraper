#!/usr/bin/env python

import unittest

from sqlalchemy import create_engine

from cscraper import Base, Session, Pdf, Link

engine = create_engine('sqlite:///:memory:')
Session.configure(bind=engine)
session = Session()

class TestScraper(unittest.TestCase):
    def setUp(self):

        Base.metadata.create_all(engine)

        self.pdf1 = Pdf('test1.pdf')
        self.pdf2 = Pdf('/test/test.pdf')
        self.link = Link('http://www.example.com/test/index.html')

    def tearDown(self):
        session.close()

    def testPdf(self):
        # Not a good test. Needs to test the query from db
        self.assertTrue(self.pdf1.url == 'test1.pdf')

    def testLink(self):
        pass

    def testPdfLinkRelationship(self):
        # Get pdf_id from self.link
        # Get pdf_url from self.link
        pass

if __name__ == '__main__':
    unittest.main()
