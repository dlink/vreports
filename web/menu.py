import sys
import os

from vweb.html import *

class Menu(object):

    def getMenu(self, current_page):

        # customize this list
        reports= [['Books', '/vreports/?r=books'],
                  ['World', '/vreports?r=world'],
                  ]

        menu_html = ''
        for name, target in reports:

            classes = 'menu-item'
            if current_page in target:
                classes += ' active-menu-item'

            link = a(name, href=target, class_=classes) + '\n'
            menu_html += link

        return div(menu_html, id='menu')

    def getLeftNav(self):

        # customize this list
        reports = [['Dashboard', '/vreports/dashboard.py'],
                   #['Other Report', '/vreports/other.py']
                   ]

        # close icon
        close_icon = span('<', title='Close left navigation',
                          id='left-nav-close', class_='left-nav-control',
                          onclick='close_left_nav()')

        # open icon
        open_icon = span('>', title='Open Left Navigation',
                         id='left-nav-open', class_='left-nav-control',
                         onclick='open_left_nav()')

        # menu
        menu = ul(''.join([li(a(i[0], href=i[1], class_='menu-item')) \
                               for i in reports]))
        left_nav = span(menu + close_icon, id='left-nav', class_='on-left')
        
        return left_nav + open_icon
