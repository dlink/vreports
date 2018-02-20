#!/usr/bin/python

from vweb.html import p

from basepage import BasePage

class Dashboard(BasePage):

    def __init__(self):
        BasePage.__init__(self, 'Dashboard')

    def getReport(self):
        return p(
            'Dashboard is empty. See '
            '<a href="http://github.com/dlink/vreports" target="_blank">'
            'VReports</a> for information about configuring Dashboard')
    
if __name__ == '__main__':
    Dashboard().go()
