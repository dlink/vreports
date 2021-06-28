import os
import sys

from flask import Flask
app = Flask(__name__)

@app.route('/')
def root():
    from nodata import NoData
    return NoData().go()

@app.route('/reports/<report_name>', methods=['GET', 'POST'])
def report(report_name):
    from reportbase import ReportBase
    return ReportBase(report_name).go()

@app.route('/test_page')
def test_page():
    from test_page import TestPage
    return TestPage().go()


#not for production
#@app.route("/showenv")
def showenv():
    import getenv
    return \
        "<h1 style='color:blue'>Nginx + gunicorn + flask + pyenv 3.9</h1>" + \
        getenv.getEnv()

if __name__ == "__main__":
    app.run(host='0.0.0.0')

