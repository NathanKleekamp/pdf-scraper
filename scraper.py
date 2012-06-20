#!/usr/bin/env python

'''
Scrapes exchanges for pdf files. Returns a csv file with each pdf in a given
section and the page(s) on which they're linked.
'''

import re
import sys
import requests

from bs4 import BeautifulSoup

# Global Variables
try:
    start = sys.argv[1]
except IndexError:
    print('You must enter a starting point, like heritage/index.html')
    start = raw_input('Enter a starting point: ')

if start[0] == '/':
    start = start[1:]

_baseurl = 'http://exchanges.state.gov/'
full_url = _baseurl+start
start = start.split('/')


def get_pdfs(soup):
    '''Obtains a list of pdfs on a given page'''
    pdf_urls = {}
    pdf_links = soup.find_all('a', href=re.compile("\.pdf$"))
    if not pdf_links:
        print('There are no PDFs on this page.')
    else:
        unique_pdfs = set([link.get('href') for link in pdf_links])
        for pdf in unique_pdfs:
            pdf_urls[pdf] = full_url
        for k, v in pdf_urls.items():
            print(k, v)


def get_urls(soup):
    '''Grabs urls to pages within the same "directory/folder"'''
    links = set()
    spider_urls = soup.find_all('a', href=re.compile("\.html$"))
    unique_links = set([link.get('href') for link in spider_urls])
    for link in unique_links:
        if start[0] in link:
            links.add(link)
    return links


def main():
    '''The work horse'''
    r = requests.get(full_url)
    soup = BeautifulSoup(r.text)
    links = set()
    pdfs = get_pdfs(soup)
    for link in get_urls(soup):
        links.add(link)


if __name__ == '__main__':
    main()
