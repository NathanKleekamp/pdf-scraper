#!/usr/bin/env python

import unittest

import os
import re
import csv
import sys
import logging
import urlparse
import lxml
import requests

from bs4 import BeautifulSoup
from sqlalchemy import create_engine, Column, Integer, String, Boolean, \
     ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref


class TestSpider(unittest.TestCase):
    pass
