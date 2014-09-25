#!/usr/bin/env python

import os
import sys

# add vreports lib to PYTHONPATH:
libdir = os.path.dirname(os.path.realpath(__file__)).replace('/web', '/lib')
sys.path.append(libdir)

from reportbase import ReportBase
ReportBase().go()

