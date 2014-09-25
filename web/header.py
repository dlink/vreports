#!/usr/local/bin/python

from vweb.html import *

LOGO = 'VReports Database Report'

class Header(object): 

    def __init__(self, title):
        self.title = title

    def getHeader(self, user):
        logo = LOGO

        # Add environment name if NOT production:
        #if self.config.environment != 'production':
        #    logo += big(" <i>(%s)</i>" % self.config.environment.title())

        if user.is_admin():
          admin = a("Admin", href="/admin.py", id="admin-link")
        else:
          admin = ""

        return div(div(logo, class_='logo') + 
                   self.title + admin, class_='header')
