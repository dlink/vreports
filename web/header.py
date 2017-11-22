#!/usr/local/bin/python

from vweb.html import *

LOGO = 'VReports'
COMPANY = 'Crowfly.net'

class Header(object): 

    def __init__(self, title):
        self.title = title

    def getHeader(self):
        return div(
            span(LOGO, id='vreports-logo') + \
            span(COMPANY, id='company-name'),
            id='header')
    
