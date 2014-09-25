import sys
import os

from vweb.html import *

class Menu(object):

    def is_current_page(self, target):
      return target in sys.argv[0]

    def htmlify(self, nav, submenu=False):
      menu = []
      for (name, target) in nav:
        if type(target) is list:
          menu.append(li(a(name, href='#') + self.htmlify(target, submenu=True)))
        elif type(target) is str:
          menu.append(li(a(name, href=target)))

      if submenu:
        return ul("".join(menu), class_="sub_menu")
      else:
        return ul("".join(menu), class_="dropdown")

    #def getMenu(self, user, show_login_info=True):
    def getMenu(self, show_login_info=True):
        reports= [
                   ['Books', 'books']
                   ]
        this_report = sys.argv[0]
        menu = self.htmlify(reports)

        if show_login_info:
            #if user:
            #  menu += div('Logged in as ' + user.display_name() + \
            #              ' &middot; ' + a('Change User', class_='signout'),
            #              class_='floatr')
            #else:
            menu += div('Not logged in', class_='floatr')

        #js = script("", type_='text/javascript', language='javascript', src='js/menufix.js')
        #js += script("", type_='text/javascript', language='javascript', src='js/jquery.dropdownPlain.js')

        #return div(menu + js, class_='menu')
        return div(menu, class_='menu')

    def get_my_reports(self, user):
      l = []
      if len(user.reports()) > 0:
        for report in user.reports():
          l.append([report.title, '/show_report.py?r=' + str(report.url_id)])
      if len(l) == 0:
        # Do not display if list is empty
        l = None
      return ['My Reports', l]
