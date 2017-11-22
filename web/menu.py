import sys
import os

from vweb.html import *

class Menu(object):

    def is_current_page(self, target):
      return target in sys.argv[0]

    def getMenu(self):
        reports= [['Books', '/?r=books'],
                  ['World', '/?r=world']
                  ]
        this_report = sys.argv[0]
        menu_html = self.getHtml(reports)
        return div(menu_html, id='nav')

    def getHtml(self, reports):
        menu = []
        for (name, target) in reports:
            if type(target) is list:
                menu.append(li(a(name, href='#') + self.htmlify(target, 
                                                          submenu=True)))
            elif type(target) is str: 
               menu.append(li(a(name, href=target, class_='menu-link')))

        return ul("".join(menu), class_="menu")

    def get_my_reports(self, user):
      l = []
      if len(user.reports()) > 0:
        for report in user.reports():
          l.append([report.title, '/show_report.py?r=' + str(report.url_id)])
      if len(l) == 0:
        # Do not display if list is empty
        l = None
      return ['My Reports', l]
