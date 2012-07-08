#!/usr/bin/env python

# sys path hack
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spider import Spider, Pdf, Link
from spider.database import Base

Session = sessionmaker()
engine = create_engine('sqlite:///test.db')


class TestScraperDb(unittest.TestCase):
    """Test case for SQLAlchemy models"""
    def setUp(self):
        """Set Up"""
        Base.metadata.create_all(engine)
        self.connection = engine.connect()
        self.trans = self.connection.begin()
        self.session = Session(bind=self.connection)

    def tearDown(self):
        """Tear down"""
        #self.trans.rollback()
        self.session.close()
        #os.remove('test.db')

    def testAddPdf(self):
        """
        Tests pdf saved to db and that pdf/links relationship works.
        """
        pdf = Pdf('test1.pdf')
        pdf.links.append(Link('http://www.example.com/test/index.html'))
        pdf.links.append(Link('http://www.example.com/test/test.html'))
        self.session.add(pdf)
        self.session.commit()
        self.assertTrue(pdf in self.session.query(Pdf).all())
        expected = ['http://www.example.com/test/index.html',
                    'http://www.example.com/test/test.html']
        actual = []
        for i in self.session.query(Pdf).all():
            for j in i.links:
                actual.append(j.url)
        self.assertEqual(expected, actual)

        # Seems like testAddPdf should be replaced with something like
        # function that actually does something.
    def test_save_pdfs(self):
        """Tests that pdfs are being saved to db"""
        #actual = self.spider.save_pdf(get_pdfs(soup))
        pass

    def testAddLink(self):
        """
        Tests that visted/unvisited links are saved to db.
        """
        link = Link('http://www.example.com/test/index.html')
        self.session.add(link)
        link_visited = Link('http://www.example.com/test/test.html',
                             visited=True)
        self.session.add(link_visited)
        self.session.commit()
        self.assertTrue(link in self.session.query(Link).all())
        self.assertTrue(link_visited in self.session.query(Link).all())
        self.assertTrue(link_visited in self.session.query(Link).filter(
                                        Link.visited==True).all())
        self.assertTrue(link not in self.session.query(Link).filter(
                                        Link.visited==True).all())


if __name__ == '__main__':
    unittest.main()
