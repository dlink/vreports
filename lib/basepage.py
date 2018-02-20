#!/usr/bin/python

import os, sys

from vweb.htmlpage import HtmlPage
from vweb.html import *

from header import Header
from menu import Menu

class BasePage(HtmlPage):
    '''Base Page for VReports'''

    def __init__(self, report_name='Base Report'):
        HtmlPage.__init__(self, report_name)
        self.report_name = report_name

        self.menu = Menu()
        self.header = Header(self.title)

        progpath = os.path.dirname(sys.argv[0])
        def versionize(file):
            timestamp = os.path.getmtime('%s/../web/%s' % (progpath, file))
            return '%s?v=%s' % (file, timestamp)

        self.javascript_src = [
            "//code.jquery.com/jquery-1.10.2.js",
            "//code.jquery.com/ui/1.11.1/jquery-ui.js",
            versionize('js/vreports.js'),
            ]
        self.style_sheets.extend(
            ['http://code.jquery.com/ui/1.10.2/themes/smoothness/' \
                 'jquery-ui.css',
             versionize('css/vreports.css'),
             ])

    def process(self):
        HtmlPage.process(self)

    def getHtmlContent(self):
        '''Return the entire HTML content of the page.
           (Without HTTP Header)
        '''
        return div(
            self.header.getHeader() + \
            div(
              self.menu.getMenu(self.report_name) + \
              self.menu.getLeftNav() + \
              span(
                self.getReportDesc() + \
                self.getReport(),
                id='report'
              ),
              id='content-container'),
            id='page-container')

    def getReportDesc(self):
        report_name = span(self.report_name, id='report-name')
        return div(report_name, id='report-header')

    def getReport(self):
        raise Exception('You must override getReport()')

if __name__ == '__main__':
    BasePage().go()
