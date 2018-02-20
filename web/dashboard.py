#!/usr/bin/python

from vweb.html import p

from basepage import BasePage

class Dashboard(BasePage):

    def __init__(self):
        BasePage.__init__(self, 'Dashboard')

    def getReport(self):
        return p(
            'This is an example site set up to demo '
            '<a href="http://github.com/dlink/vreports" target="_blank">'
            'VReports</a>') + \
            p('See Sample reports Books, and World above.')
    
if __name__ == '__main__':
    Dashboard().go()
