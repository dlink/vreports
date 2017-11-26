import sys
import os

from vweb.html import *

class Menu(object):

    def getMenu(self, current_page):
        reports= [['Books', '/vreports/?r=books'],
                  ['World', '/vreports?r=world']
                  ]
        menu_html = ''
        for name, target in reports:

            classes = 'menu-item'
            if current_page in target:
                classes += ' active-menu-item'

            link = a(name, href=target, class_=classes) + '\n'
            menu_html += link

        return div(menu_html, id='menu')
