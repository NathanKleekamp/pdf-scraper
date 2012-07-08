'''
Version 0.2
Spiders sections of J1 or Exchanges looking for pdfs and reports on
the PDF's location throughout the section.

By design, this script will not spider links offsite or the entirety
of those sites. Future versions may support spidering whole sites.
'''

from .database import Link, Pdf
from .spider import Spider