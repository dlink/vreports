import os
import sys

from reportbase import ReportBase

from flask import Flask
app = Flask(__name__)

@app.route("/")
def root():
    return ReportBase().go()

#@app.route("/showenv")
#def showenv():
#    import getenv
#    return \
#        "<h1 style='color:blue'>Nginx + gunicorn + flask + pyenv 3.9</h1>" + \
#        getenv.getEnv()

if __name__ == "__main__":
    app.run(host='0.0.0.0')

