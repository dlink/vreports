#!/usr/local/bin/python

import os
import yaml

from vlib import db
from vlib.sqlutils import pretty_sql
from vlib.utils import list2csv, format_date
from vlib.odict import odict
from vlib.entities import toEntity

from vweb.htmlpage import HtmlPage
from vweb.htmltable import HtmlTable
from vweb.html import *

from header import Header
from menu import Menu

from reportcolumns import ReportColumns
from reportcontrols import ReportControls
from reportsqlpanel import ReportSqlPanel
from reportsqlbuilder import ReportSqlBuilder

from datetime import datetime
#from dateutil.relativedelta import relativedelta

DEBUG_SAVE_REPORT = 0

class VReportException(Exception): pass

class ReportBase(HtmlPage):
    '''Base Webpage Report
       Dynamic Reporting
    '''

    def __init__(self):
        HtmlPage.__init__(self, 'Untitled')
        if 'r' not in self.form:
            raise VReportException('No report name passed')

        self.report_name = self.form['r'].value
        self.title = self.report_name.title()
        self.loadParams()

        self.debug_cgi      = self.params.debug_cgi
        self.db             = db.Db(self.params.database)
        self.reportColumns  = ReportColumns(self.params)
        self.reportControls = ReportControls(self.params)
        self.sqlBuilder     = ReportSqlBuilder(self.params, self.reportColumns)
        self.reportSqlPanel = ReportSqlPanel(self.params, self.sqlBuilder)

        self.menu = Menu()
        self.header = Header(self.title)

        self.javascript_src = [
            "//code.jquery.com/jquery-1.10.2.js",
            "//code.jquery.com/ui/1.11.1/jquery-ui.js",
            'js/report.js',
            ]
        self.style_sheets.extend([
            "http://code.jquery.com/ui/1.10.2/themes/smoothness/jquery-ui.css",
            'css/main.css',
            'css/report_controls.css',
            'css/column_chooser.css',
            'css/report_sql_panel.css'
            ])
        
    def loadParams(self):
        '''Load parameters files
        '''
        pdir = os.environ['PARAMETER_FILES_DIR']

        # load yaml parameter files:
        self.params = odict()
        for c in ['main', 'columns', 'controls', 'table_joins']:
            filepath = "%s/%s/%s.yaml" %(pdir, self.report_name, c)
            self.params.update(dict2odict(yaml.load(open(filepath))))

        # fill in some blank defaults:
        for column in self.params.columns:
            if 'display' not in column:
                column.display = column.name.replace('_', ' ').title()
            if 'select' not in column:
                column.select = '%s.%s' % (self.params.base_table_alias,
                                           column.name)
        for control in self.params.controls:
            if 'display' not in control:
                control.display = control.name.replace('_', ' ').title()
            if 'type' not in control:
                control.type = 'string'
            if 'default' not in control:
                if control.type in ('integer', 'menu'):
                    control.default = 0
                else:
                    control.default = ''

    def getDb(self):
        return db.Db(self.params.database)

    # Process Inbound parameters:

    def process(self):
        HtmlPage.process(self)

        # Standardize input format (whether loaded from DB or GET)
        #shared_form = {}
        #if self.report and len(self.form.keys()) <= 2 and 'r' in self.form:
        #  shared_form = self.report.params
        #  for key in shared_form:
        #    # Convert relative dates into absolute dates
        #    now = datetime.now()
        #    if str(shared_form[key]).find("#DAYSAGO:") == 0:
        #      days_ago = int(shared_form[key].split(':')[1])
        #      shared_form[key] = (now - relativedelta(days=days_ago)).strftime("%Y-%m-%d")
        #    elif str(shared_form[key]).find("#MONTHSAGO:") == 0:
        #      months_ago = int(shared_form[key].split(':')[1])
        #      shared_form[key] = (now - relativedelta(months=months_ago)).strftime("%Y-%m-%d")
        #    elif str(shared_form[key]).find("#YEARSAGO:") == 0:
        #      years_ago = int(shared_form[key].split(':')[1])
        #      shared_form[key] = (now - relativedelta(years=years_ago)).strftime("%Y-%m-%d")
        #    elif str(shared_form[key]).find("#CURRENT:MONTH") == 0:
        #      shared_form[key] = datetime(now.year, now.month, 1).strftime("%Y-%m-%d")
        #    elif str(shared_form[key]).find("#CURRENT:YEAR") == 0:
        #      shared_form[key] = datetime(now.year, 1, 1).strftime("%Y-%m-%d")
        #else:

        shared_form = {}
        for field in self.form:
            shared_form[field] = self.form[field].value

        # Controls: Init
        for control in self.params.controls:
            # Reads user setting or set default values
            if control.name in shared_form:
                control.value = shared_form[control.name].strip()
            else:
                control.value = control.default

            # Convert Integers
            if control.type in ('integer', 'menu'):
                control.value = int(control.value)
                
        # Pager Control: Init
        if 'page_num' in shared_form:
            self.params.page_num = int(shared_form['page_num'])
            if self.params.page_num < 1:
                self.params.page_num = 1
        else:
            self.params.page_num = 1

        # Controls Show/Hide: Init
        if 'show_controls' in shared_form:
            self.params.show_controls = shared_form['show_controls']
        else:
            self.params.show_controls =  0
            
        # Columns Chooser: Show/Hide Init
        if 'show_chooser' in shared_form:
            self.params.show_chooser = shared_form['show_chooser']
        else:
            self.params.show_chooser = 0

        # Show SQL: Show/Hide Init
        if 'show_sql_panel' in shared_form:
            self.params.show_sql_panel = shared_form['show_sql_panel']
        else:
            self.params.show_sql_panel = 0

        # Column Chooser:  Init - Read user settings or set defaults
        found_values = False
        for column in self.params.columns:
            #if column.get('type') != 'separator':
            if '%s_column' % column.name in shared_form \
                   and shared_form['%s_column' % column.name]:
                column.selected = True
                found_values = True
        if not found_values:
            for column in self.params.columns:
                if column.get('default'):
                    column.selected = True

        # Column report_links init:
        # report_key column must be selected
        for column in self.reportColumns.getSelectedColumns():
            if column.get('report_link'):
                self.reportColumns.getColumn(column.report_key).selected = True

        # Set Group_by
        if 'group_by' in shared_form:
            group_by_name = shared_form['group_by']
            #self.debug_msg = p(group_by_name)
            for column in self.params.columns:
                if group_by_name == column.name:
                    self.params.group_by = column
                    column.selected = True
                    break
            if not self.params.group_by:
                raise Exception('Unrecognized group_by value: %s' % group_by)
            
        # clear controls if nec.
        if 'clear_cntrls' in shared_form:
            for control in self.params.controls:
                control.value = control.default
            if 'group_by' in self.params:
                del self.params.group_by


        # sort_by
        # TO DO: refactor this mess
        sort_by = None
        if 'sort_by' in shared_form:
            sort_by = shared_form['sort_by']
            if sort_by == ':': # ignore blanks
                sort_by = None
            else:
                col, dir = sort_by.split(':')
                # ignore value no longer in form
                if col not in [c.name for c in
                               self.reportColumns.getSelectedColumns()]:
                    sort_by = None
        if not sort_by and 'group_by' not in self.params:
            # default:
            sort_by = self.params.get('sort_by', '1:desc')
        if sort_by:
            sort_column, sort_direction = sort_by.split(':')
            if sort_column not in [c.name for c in \
                                   self.reportColumns.getSelectedColumns()]:
                sort_column = 1
        else:
            sort_column = sort_direction = ''
        self.params.sort_column    = sort_column
        self.params.sort_direction = sort_direction

        # s_sort_by
        s_sort_by = None
        if 's_sort_by' in shared_form:
            s_sort_by = shared_form['s_sort_by']
            
            if s_sort_by == ':': # ignore blanks
                s_sort_by = None
            else:
                col, dir = s_sort_by.split(':')
                # ignore value no longer in form
                if col not in [c.name for c in
                               self.reportColumns.getSelectedColumns()]:
                    s_sort_by = None
        if not s_sort_by and 'group_by' in self.params:
            # defaults
            s_sort_by ='%s:asc' \
                          % self.reportColumns.getSelectedColumns()[0].name
        if s_sort_by:
            s_sort_column, s_sort_direction = s_sort_by.split(':')
        else:
            s_sort_column = s_sort_direction = ''
        self.params.s_sort_column    = s_sort_column
        self.params.s_sort_direction = s_sort_direction

    def debug_save_report(self):
      from report_columns import ReportColumnsError
      from report_controls import ReportControlsError

      report = self.report
      self.debug_msg += '<b>report values:</b> <br/>'
      self.debug_msg += 'title: %s<br/>' % report.title
      self.debug_msg += 'param_file: %s<br/>' % report.param_file
      self.debug_msg += 'created_at: %s<br/>' % report.created_at

      self.debug_msg += 'params:<br/>'
      for k, v in report.params.items():
          # check
          info = ''
          # check columns
          if '_column' in k:
              column = k.replace('_column', '')
              try:
                  x = self.reportColumns.getColumn(column)
              except ReportColumnsError, e:
                  info = ' <font color="red">[%s]</font>' % e
          # skip csv and_sort by columns:
          elif k == 'csv' or 'sort_by' in k:
              pass
          # check controls:
          else:
              try:
                  x = self.reportControls.getControl(k)
              except ReportControlsError, e:
                  info = ' <font color="red">[%s]</font>' % e
          self.debug_msg += '&nbsp; &nbsp; %s: %s%s<br/>' % (k,v, info)

            
    # Level I

    def getHtmlContent(self):
        '''Return the entire HTML content of the page.
           (Without HTTP Header)
        '''
        return div(
            self.header.getHeader() + \
            self.menu.getMenu(show_login_info=True) + \
            div(
              self.getControlOptions() + \
              self.reportSqlPanel.getSqlPanel() + \
              self.reportControls.getControls() + \
              self.reportColumns.getColumnChooser() + \
              self.getHiddenFields() + \
              self.getReportDesc() + \
              self.getReportTable() + \
              self.getReportTableFooter(),
              id='content') + \
            self.help() + \
            self.save_panel(),
            id='page_container')

    def getCsv(self):
        o = ''
        o += ','.join([c.display for
                       c in self.reportColumns.getSelectedColumns()]) + '\n'
        o += list2csv(self.getData(target='csv'))
        return o

    def help(self):
      if 'help_file' in self.params:
        return div(open(self.params.help_file, 'r').read(), id='help')
      else:
        return ""

    # Level II
    
    def getControlOptions(self):
        return div(''.join([self.reportControls.getShowButton(),
                            self.reportColumns.getShowButton(),
                            self.reportSqlPanel.getShowButton()]),
                   id='report_options')
    
    def getHiddenFields(self):
        SHOW_HIDDEN=0
        if SHOW_HIDDEN:
            itype      = 'text'
            page_num = 'page_num'
            show_controls = 'show_controls'
            show_chooser  = 'show_chooser'
            show_sql_panel = 'show_sql_panel'
            sort_by = 'sort_by'
            s_sort_by = 's_sort_by'
            clear_cntrls = 'clear_cntrls'
        else:
            itype = 'hidden'
            page_num = show_controls = show_chooser = show_sql_panel = \
                       sort_by = s_sort_by = clear_cntrls = '' 

        show_report_params = ''
        if 'r' in self.form:
          show_report_params += input(name='r', type=itype,
                                      value=self.form['r'].value)
        if 'u' in self.form:
          show_report_params += input(name='u', type=itype,
                                      value=self.form['u'].value)

        return page_num + input(name='page_num', type=itype,
                                value=self.params.page_num) + \
               show_controls + input(name='show_controls', type=itype,
                                     value=self.params.show_controls) + \
               show_chooser + input(name='show_chooser',
                                    type=itype,
                                    value=self.params.show_chooser) + \
               show_sql_panel + input(name='show_sql',
                                      type=itype,
                                      value=self.params.show_sql_panel) + \
               sort_by + input(name='sort_by', type=itype,
                               value="%s:%s" % (self.params.sort_column,
                                                self.params.sort_direction)) +\
               s_sort_by + input(name='s_sort_by', type=itype,
                                   value="%s:%s" \
                                   % (self.params.s_sort_column,
                                      self.params.s_sort_direction)) +\
               clear_cntrls + input(name='clear_cntrls', type=itype) +\
               show_report_params
            
    def getReportDesc(self):
        filters = []
        for control in self.params.controls:
            if control.get('value'):
                if control.type == 'menu':
                    value = control.menu[control.value]
                else:
                    value = control.value
                filters.append("%s: %s" % (control.display, value))
        if self.params.get('group_by'):
            filters.append('Summarized by: %s' % self.params.group_by.display)
                           
        filter_desc = '; &nbsp; '.join(filters)
        if not filter_desc:
            filter_desc = 'All'
                
        return div(' &nbsp; - &nbsp; '.join([self.params.report_title,
                                             filter_desc,
                                             self.getRowCountDesc(),
                                             self.getPager(),
                                             self.getCsvButton(),
                                             self.getSaveButton()]),
                   id='report_description_container',
                   style='clear: both')

    def getPager(self):
        # previous button
        if self.params.page_num == 1:
            prev = ''
        else:
            prev_text = '&lt;&lt;Prev'
            prev = input(name='prev', type='button',
                         value=prev_text, onclick='go_to_prev_page()')

        # next button
        if self.params.page_num * self.params.display_num_rows \
               > self.getRowCount():
            next = ''
        else:
            next_text = 'Next&gt;&gt;'
            next = input(name='next', type='button',
                         value=next_text, onclick='go_to_next_page()')
            
        if prev and next:
            return "%s%s" % (prev, next)
        elif next:
            return next
        else:
            return prev

    def getSaveButton(self):
      return input(name='save', type='button',
                   value='Save to My Reports', onclick='save_report()')
    
    def getRowCountDesc(self):
        row_count = self.getRowCount()
        if row_count <= self.params.display_num_rows:
            row_count_desc = '%s Rows' % row_count
        else:
            x = self.params.display_num_rows * (self.params.page_num-1) + 1
            y = x + self.params.display_num_rows - 1
            if y > row_count:
                y = row_count
            row_count_desc = 'Rows {x} - {y}, of {z}'.format(
                x=x, 
                y=y,
                z="{:,}".format(row_count))
        return row_count_desc

    def getReportTable(self):
        table = HtmlTable(class_='report_table')        
        table.addHeader(self.getColumnHeaders())
        for row in self.getData():
            #table.addRow(row)
            # experimenting with nobr 9/3/2013 -dvl
            table.addRow(["<nobr>%s</nobr>" % x for x in row])

        # top valign header:
        table.setRowVAlign(1, 'top')
        
        # right align number:
        col = 1
        for column in self.reportColumns.getSelectedColumns():
            if column.get('type') in ('number', 'integer', 'money', 'percent'):
                table.setColAlign(col, 'right')
            col += 1
                
        return table.getTable()

    def getReportTableFooter(self):
        return div(' &nbsp; - &nbsp; '.join([self.getRowCountDesc(),
                                             self.getPager()]),
                   id='report_table_footer')


    def getColumnHeaders(self):
        headers = []
        onclick = 'set_s_sort' if 'group_by' in self.params else 'set_sort'
        for column in self.reportColumns.getSelectedColumns():
            sort_indicator, sort_direction = self.getSortIndicator(column)
            cell = a("%s%s" % (column.display, sort_indicator),
                     onclick="%s('%s', '%s')"
                     % (onclick, column.name, sort_direction))
            headers.append(cell)
        return headers
    
    def getSortIndicator(self, column):
        indicator = ''
        direction = 'asc'
        if self.params.get('group_by'):
            sort_column    = self.params.s_sort_column
            sort_direction = self.params.s_sort_direction
        else:
            sort_column    = self.params.sort_column
            sort_direction = self.params.sort_direction
        if column.name == sort_column:
            icon_file = 'images/sort_%s.png' % sort_direction
            indicator = img(src=icon_file)
            direction = 'desc' if sort_direction =='asc' else 'asc'
        return indicator, direction

    # Data Level:
    
    def getData(self, target='html'):
        sql = self.sqlBuilder.getSQL(limited=target!='csv')
        if self.params.debug_sql:
            self.debug_msg += p("SQL: %s" % pretty_sql(sql, True))

        table = []
        for row in self.db.query(sql):
            row2 = []
            for column in self.reportColumns.getSelectedColumns():
                value = row[column.name]
                if isinstance(value, basestring):
                    value = toEntity(value)
                if value is None:
                    value = ''
                if column.get('type') == 'money' and (value or value==0):
                    value = "{:,.2f}".format(value)
                elif column.get('type') == 'percent':
                    value = "{:,.2f}%".format(value*100)
                elif column.get('type') == 'date' and value:
                    value = format_date(value)
                if target == 'html' and column.get('html'):
                    value = column.html % value
                if target == 'html' and column.get('link'):
                    value = a(value, href=column.link % value, target='_blank')

                # report_link and report_key allows linking into other reports
                if target == 'html' and column.get('report_link') and \
                   not self.params.get('group_by') and value and value != 'No':
                    report_link = column['report_link']
                    report_key  = column['report_key']
                    value = a(value, href='%s?%s=%s' % (report_link,
                                                        report_key,
                                                        row[report_key]),
                              target='_blank')
                row2.append(value)
            table.append(map(str, row2))
        return table
    
    def getRowCount(self):
        if '_row_count' not in self.__dict__:
            sql = self.sqlBuilder.getCountSQL()
            if self.params.debug_sql:
                self.debug_msg += p("Count SQL: %s" % pretty_sql(sql, True))
            self._row_count = self.db.query(sql)[0]['count']
        return self._row_count

    def save_panel(self):
      report_title = ""
      #if self.report:
      #  report_title = self.report.param_file.split("/")[0]
      return """
        <div id="save-panel">
          <div id="save-panel-header">
            <div class="cancel">x</div>
            Save Report
          </div>
          <div id="save-panel-body">
            <p>By saving this report, you can have quick access to it from now on through the "My Reports" menu. Just give it a name so you can identify it.</p>
            <div id="questions"></div>
            <input type="hidden" name="report_title" value="%s">
            <label for="custom_report_name">Name your report:</label>
            <input type="text" name="custom_report_name" id="custom_report_name">
            <input type="button" value="Save Report">
          </div>
        </div>
      """ % report_title

# Helpers

def dict2odict(src_dict):
    '''Return an dict converted recursively into an odict'''
    o = odict()
    for k,v in src_dict.items():
        if isinstance(v, dict):
            o[k] = dict2odict(v)
        elif isinstance(v, list):
            o[k] = []
            for l in v:
                if isinstance(l, dict):
                    o[k].append(dict2odict(l))
                else:
                    o[k].append(l)
        else:
            o[k] = v
    return o
