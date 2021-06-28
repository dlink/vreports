import os
import sys

from reportbase import ReportBase
from nodata import NoData

from flask import Flask
app = Flask(__name__)

@app.route('/')
def root():
    return NoData().go()

@app.route('/report/<report_name>')
def report(report_name):
    return ReportBase(report_name).go()

#not for production
#@app.route("/showenv")
def showenv():
    import getenv
    return \
        "<h1 style='color:blue'>Nginx + gunicorn + flask + pyenv 3.9</h1>" + \
        getenv.getEnv()

if __name__ == "__main__":
    app.run(host='0.0.0.0')

