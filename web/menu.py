import sys
import os

from vweb.html import *

class Menu(object):

    def getMenu(self):
        reports= [['Books', '?r=books'],
                  ['World', '?r=world'],
                  ]
        menu_html = self.getHtml(reports)
        return div(menu_html, class_='menu')

    def getHtml(self, reports):
        menu = []
        for (name, target) in reports:
            if type(target) is list:
                menu.append(a(name, href='#') + self.htmlify(target, 
                                                              submenu=True))
            elif type(target) is str: 
               menu.append(input(name=name, class_='btn btn-primary btn-sm', type='button',
                                 value=name, onclick="location.href='%s'" % target))

        return div(' &nbsp; ' * 3 + \
                   " &nbsp; ".join(menu), class_='form-group menu')
