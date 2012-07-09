# sys.path hack
import os
import sys
sys.path.insert(0, os.path.abspath('../'))

import unittest
import requests

from bs4 import BeautifulSoup

from spider import Spider, Pdf, Link, Session

session = Session()

class TestSpider(unittest.TestCase):
    """Test case for the Spider clas"""
    def setUp(self):
        """Set up"""
        self.start = 'http://exchanges.state.gov/heritage/index.html'
        self.r = requests.get(self.start)
        self.spider = Spider(self.start, blacklist=(
                                         os.path.abspath('blacklist.txt')))
        self.soup = BeautifulSoup(self.r.text)

    def test_get_links(self):
        """Tests only links are being collected"""
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

    def test_save_pdfs(self):
        """Tests that pdfs are being saved to db"""
        pdf = Pdf('test.pdf')
        session.add(pdf)
        session.commit()
        actual = session.query(Pdf).filter(Pdf.url==('test.pdf')).first().url
        self.assertTrue('test.pdf' == actual)

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
        #actual = self.spider.crawl()
        pass

    def tearDown(self):
        """Tear down"""
        #os.remove('database.db')
        pass


if __name__ == '__main__':
    unittest.main()