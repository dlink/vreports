#!/usr/local/bin/python

from vweb.html import *

LOGO = 'VReports Database Report'

class Header(object):

    def __init__(self, title):
        self.title = title

    def getHeader(self):
        logo = div(LOGO, class_='text-element')
        report_name = center(h1(self.title))
        return div(logo + report_name, class_='header')
