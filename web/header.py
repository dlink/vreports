#!/usr/local/bin/python

from vweb.html import *

LOGO = 'VReports Database Report'

class Header(object):

    def __init__(self, title):
        self.title = title

    def getHeader(self):
        logo = LOGO
        return div('\n'.join([div(logo, class_='text-element'),
                              p(strong(self.title),
                                class_='text-center text-element text-element-lg')]),
                   class_='header'
                   )
