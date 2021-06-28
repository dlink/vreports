import os
import sys

def getEnv():

    basedir = '/'.join(os.environ['VIRTUAL_ENV'].split('/')[0:-1])
    o = ''
    o += "<h2>OS Environment</h2>"
    o += '<p>Python Version: %s</p>' % sys.version
    o += '<p>Python Prefix: %s</p>' % sys.prefix
    o += '<p>sys.argv: %s</p>' % sys.argv
    o += '<p>basedir: %s</p>' % basedir
    o += '<p>Python Sys.Path:<br/>%s</p>' % ['%s<br/>' % p for p in sys.path]
    o += "<table border='1' cellpadding='2' cellspacing='0'>"
    
    keys = list(os.environ.keys())
    keys.sort()
    for k in keys:
    	v = os.environ[k]
    	if not v:
           v = "&nbsp;"
    	o += "  <tr> <td valign='top'><font color='blue'>%s</font></td> " \
            "<td>%s</td> </tr>" % (k, v)
    o += "</table>"
    return o
