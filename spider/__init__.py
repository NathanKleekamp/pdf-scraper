'''
Version 0.2
Spiders sections of J1 or Exchanges looking for pdfs and reports on
the PDF's location throughout the section.

By design, this script will not spider links offsite or the entirety
of those sites. Future versions may support spidering whole sites.
'''

from creds import my_engine

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


# Setting up the database and database classes
engine = create_engine(my_engine)
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


from .database import Link, Pdf
from .spider import Spider, GrabSoup, DataWrite