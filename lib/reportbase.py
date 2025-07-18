#!/usr/local/bin/python

import os, sys
import yaml

from flask import request

from vlib import db
from vlib.sqlutils import pretty_sql
from vlib.utils import list2csv, format_date
from vlib.odict import odict
from vlib.entities import toEntity

from vweb.htmltable import HtmlTable
from vweb.html import *

from header import Header
from menu import Menu

from basepage import BasePage
from reportfilters import ReportFilters
from reportsummaries import ReportSummaries
from reportlimits import ReportLimits
from reportcolumns import ReportColumns
from reportsqlpanel import ReportSqlPanel
from reportsqlbuilder import ReportSqlBuilder

from datetime import datetime

NUM_GROUP_BYS = 10

class VReportException(Exception): pass

class ReportBase(BasePage):
    '''Base Webpage Report
       Dynamic Reporting
    '''

    default_images = {
        'loading': '/images/loading.gif',
        'sort_asc': '/images/sort_asc.png',
        'sort_desc': '/images/sort_desc.png',
    }

    def __init__(self, report_name=None, allow_download=True,
                 additional_conf_file=None):
        '''Constructor:
              report_name    - Name of page
              allow_download - Add [csv download] button or not
              additional_conf_file - Can be used to define database
        '''
        BasePage.__init__(self, 'Untitled')
        self.nodata = False

        if report_name:
            self.report_name = report_name
        elif 'r' in self.form:
            self.report_name = self.form['r'].value
        else:
            self.nodata = True
            print('Location: nodata.py') # <-- Exit
            return

        self.title = self.report_name.title()
        self.allow_download = allow_download
        self.additional_conf_file = additional_conf_file
        self.loadParams()

        self.debug_form     = self.params.debug_form
        self.db             = db.Db(self.params.database)
        self.reportFilters  = ReportFilters(self.params)
        self.reportSummaries= ReportSummaries(self.params)
        self.reportLimits   = ReportLimits(self.params)
        self.reportColumns  = ReportColumns(self.params)
        self.sqlBuilder     = ReportSqlBuilder(self.params, self.reportColumns)
        self.reportSqlPanel = ReportSqlPanel(self.params, self.sqlBuilder)

        if not hasattr(self, 'images'):
            self.images = self.default_images

    @property
    def pdir(self):
        return os.environ['PARAMETER_FILES_DIR']

    def loadParams(self):
        '''Load parameters files'''

        # init params
        self.params = odict()
        
        # bring in VCONF if exists (for default db values)
        if 'VCONF' in os.environ:
            self.params = dict2odict(yaml.safe_load(open(os.environ['VCONF'])))

        # bring in additional_conf_file if exists
        if self.additional_conf_file:
            self.params = dict2odict(yaml.safe_load(open(self.additional_conf_file)))

        # init num_group_bys
        self.params['num_group_bys'] = NUM_GROUP_BYS
        
        # load yaml parameter files:
        for c in ['main', 'columns', 'controls', 'table_joins']:
            filepath = "%s/%s/%s.yaml" %(self.pdir, self.report_name, c)
            self.params.update(dict2odict(yaml.safe_load(open(filepath))))

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
        '''Pre-render form parameter processing'''
        if self.nodata: return

        BasePage.process(self)

        shared_form = {}
        for field in self.form:
            shared_form[field] = self.form[field]

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

        # Set Group_by
        self.params.group_bys = []
        for n in range(1, self.params.num_group_bys+1):
            gbn = 'group_by_%s' % n
            group_by_name = None
            if gbn in shared_form:
                group_by_name = shared_form[gbn]
            elif gbn in self.params:
                group_by_name = self.params[gbn]
            if group_by_name:
                found = 0
                for column in self.params.columns:
                    if group_by_name == column.name:
                        self.params.group_bys.append(column)
                        column.selected = True
                        found = 1
                        break
                if not found:
                    raise Exception('Unrecognized group_by value: %s'
                                    % group_by_name)

        # Set show_totals
        if 'show_totals' in shared_form:
            self.params.show_summary_totals = int(shared_form['show_totals'])
        else:
            self.params.show_summary_totals = 1

        # Column report_links init:
        # report_key column must be selected
        for column in self.reportColumns.getSelectedColumns():
            if column.get('report_link'):
                self.reportColumns.getColumn(column.report_key).selected = True

        # clear controls if nec. (deprecated - now done in JS)
        #if 'clear_cntrls' in shared_form:
        #    for control in self.params.controls:
        #        control.value = control.default
        #    for n in range(1, self.params.num_group_bys+1):
        #        gbn = 'group_by_%s' % n
        #        if gbn in self.params:
        #            del self.params[gbn]

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
        if not sort_by and not self.params.group_bys:
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
        if not s_sort_by and self.params.group_bys:
            # defaults
            s_sort_by ='%s:desc' \
                          % self.reportColumns.getSelectedColumns()[0].name
        if s_sort_by:
            s_sort_column, s_sort_direction = s_sort_by.split(':')
        else:
            s_sort_column = s_sort_direction = ''
        self.params.s_sort_column    = s_sort_column
        self.params.s_sort_direction = s_sort_direction

        # limit
        if 'limit' in shared_form:
            self.params.display_num_rows = int(shared_form['limit'])

    # Level I

    def getHtmlContent(self):
        '''Return the entire HTML content of the page.
           (Without HTTP Header)
        '''
        if self.nodata: return ''

        return div(
            self.header.getHeader() + \
            div(
              self.menu.getMenu(self.report_name) + \
              self.menu.getLeftNav() + \
              span(
                self.getCustomizeReportPanel() + \
                self.getHiddenFields() + \
                self.getLoadingIndicator() + \
                self.getReportDesc() + \
                self.reportSqlPanel.getSqlPanel() + \
                self.getReportTable() + \
                self.getReportTableFooter(),
                id='report'
              ),
              id='content-container'),
            id='page-container')

    def getCsv(self):
        o = ''
        o += ','.join([c.display for
                       c in self.reportColumns.getSelectedColumns()]) + '\n'
        if self.params.group_bys and self.params.show_summary_totals:
            o += list2csv([self.getTotals(target='csv')])
        o += list2csv(self.getData(target='csv'))
        return o

    def help(self):
      if 'help_file' in self.params:
        return div(open(self.params.help_file, 'r').read(), id='help')
      else:
        return ""

    # Level II
    
    def getCustomizeReportPanel(self):
        submit_button = a('Submit', id='customize-report-submit-button',
                          class_='vbutton')
        cancel_button = a('Cancel', id='customize-report-cancel-button',
                          class_='vbutton')

        button_area = div(submit_button + cancel_button,
                          id='customize-report-buttons')

        panel = div(
            span(self.params.report_title, id='customize-report-header') + \
            a('X', href="#", class_="close", id='close') + \
            div(self.reportFilters.getControls() + \
                self.reportSummaries.getControls() + \
                self.reportLimits.getControls(),
                id='filters-and-summaries-container'
            ) + \
            self.reportColumns.getColumnChooser() + \
            button_area,
            id='customize-report-panel')

        return div(panel, id='customize-report-panel-wrapper')

    def getHiddenFields(self):
        SHOW_HIDDEN=0
        if SHOW_HIDDEN:
            itype      = 'text'
            page_num = 'page_num'
            show_sql_panel = 'show_sql_panel'
            sort_by = 'sort_by'
            s_sort_by = 's_sort_by'
            limit = 'limit'
            clear_cntrls = 'clear_cntrls'
        else:
            itype = 'hidden'
            page_num = show_sql_panel = sort_by = s_sort_by = limit = \
                clear_cntrls = ''

        show_report_params = ''
        if 'r' in self.form:
          show_report_params += input(name='r', type=itype,
                                      value=self.form['r'].value)
        if 'u' in self.form:
          show_report_params += input(name='u', type=itype,
                                      value=self.form['u'].value)

        return page_num + input(name='page_num', type=itype,
                                value=self.params.page_num) + \
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
               limit + input(name='limit', type=itype,
                             value=self.params.display_num_rows) +\
               clear_cntrls + input(name='clear_cntrls', type=itype) +\
               show_report_params
            
    def getLoadingIndicator(self):
        return div(img(src=self.images['loading'], id="loading-indicator"),
                   id="loading-indicator-wrapper")

    def getReportDesc(self):
        # get filter description
        filters = []
        for control in self.params.controls:
            if control.get('value'):
                if control.type == 'menu':
                    value = control.menu[control.value]
                else:
                    value = control.value
                filters.append("%s: %s" % (control.display, value))
        if self.params.group_bys:
            filters.append('Summarized by: %s' % ', '.join(
                    [c.display for c in self.params.group_bys]))
                           
        filter_desc = '; &nbsp; '.join(filters)
        if not filter_desc:
            filter_desc = 'All'

        # get addl buttons
        addl_buttons = [
            a('Customize Report', id='customize-report-button',
              class_='vbutton'),
            a('Show SQL', id='show-sql-button', class_='vbutton'),
            self.getCsvButton()]

        # assign ind. spans
        report_name = span(self.params.report_title, id='report-name')
        report_description = span(filter_desc, id='report-description')
        report_paging_info = span(self.getRowCountDesc(),
                                  id='report-paging-info')
        report_paging_controls = span(self.getPager(),
                                      id='report-paging-controls')
        report_addl_buttons = ' '.join(addl_buttons)
        
        # put it together
        row1 = div(
            report_addl_buttons + \
            report_paging_controls,
            id='report-buttons')

        row2 = div(
            report_name + \
            report_description + \
            report_paging_info,
            id='report-header-text')
        return div(row1 + row2, id='report-header')

    def getPager(self):
        # previous button
        if self.params.page_num == 1:
            prev = ''
        else:
            prev_text = 'Previous'
            prev = a(prev_text, id='prev-button', class_='vbutton green',
                     onclick='go_to_prev_page()')

        # next button
        if self.params.page_num * self.params.display_num_rows \
               > self.getRowCount():
            next = ''
        else:
            next_text = 'Next'
            next = a(next_text, id='next-button', class_='vbutton green',
                     onclick = 'go_to_next_page()')
            
        if prev and next:
            return "%s%s" % (prev, next)
        elif next:
            return next
        else:
            return prev

    def getCsvButton(self):
        '''This code copied from vweb/htmlpage.py and tweaked

           Return a 'Download CSV' button that can be used on the page
           Uses a hidden field called 'csv'
           Uses javascript to reset the value of that field.
        '''
        if not self.allow_download:
            return ''

        reset_js = 'function(){document.form1.csv.value=0}'
        return script('setInterval(%s,''500)') % reset_js + \
               input(name='csv', type='hidden', value='0') + \
               a('Download CSV', id='download-csv', class_='vbutton orange',
                 onclick='document.form1.csv.value=1; document.form1.submit()')

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
        table = HtmlTable(class_='vtable')
        table.addHeader(self.getColumnHeaders())
        if self.params.group_bys and self.params.show_summary_totals:
            table.addRow(self.getTotals())
            table.setRowClass(table.rownum, 'totals_row')

        for row in self.getData():
            #table.addRow(row)
            # experimenting with nobr 9/3/2013 -dvl
            table.addRow(["<nobr>%s</nobr>" % x for x in row])

        # top valign header:
        table.setRowVAlign(1, 'top')
        
        # right align number / percent cells
        col = 1
        for column in self.reportColumns.getSelectedColumns():
            if column.get('type') in ('number', 'integer', 'money', 'dollars',
                                      'round_dollars', 'percent'):
                table.setColAlign(col, 'right')

            if column.get('type') == 'percent':
                table.setColClass(col, 'vpercent')

            if column.get('class'):
                table.setColClass(col, column['class'])
            col += 1

        return div(table.getTable(), class_='vtable_float_header')

    def getReportTableFooter(self):
        
        return div(' &nbsp; - &nbsp; '.join([self.getRowCountDesc(),
                                             self.getPager()]),
                   id='report_table_footer')


    def getColumnHeaders(self):
        headers = []
        onclick = 'set_s_sort' if self.params.group_bys else 'set_sort'
        for column in self.reportColumns.getSelectedColumns():
            sort_indicator, sort_direction = self.getSortIndicator(column)
            cell = a("%s%s" % (column.display, sort_indicator),
                     onclick="%s('%s', '%s')"
                     % (onclick, column.name, sort_direction))
            headers.append(cell)
        return headers
    
    def getSortIndicator(self, column):
        indicator = ''
        if column.get('type') == 'string':
            direction = 'asc'
        else:
            direction = 'desc'
        if self.params.group_bys:
            sort_column    = self.params.s_sort_column
            sort_direction = self.params.s_sort_direction
        else:
            sort_column    = self.params.sort_column
            sort_direction = self.params.sort_direction
        if column.name == sort_column:
            icon_name = f'sort_{sort_direction}'
            indicator = img(src=self.images[icon_name])
            direction = 'desc' if sort_direction =='asc' else 'asc'
        return indicator, direction

    # Data Level:
    
    def getData(self, target='html', totals=0):
        if totals:
            sql = self.sqlBuilder.getTotalsSQL()
        else:
            sql = self.sqlBuilder.getSQL(limited=target!='csv')
        if self.params.debug_sql:
            self.debug_msg += p("SQL: %s" % pretty_sql(sql, True))

        table = []
        for row in self.db.query(sql):
            row2 = []
            for column in self.reportColumns.getSelectedColumns():
                value = row[column.name]
                if isinstance(value, str):
                    if target == 'html':
                        value = toEntity(value)
                if value is None:
                    value = ''
                if column.get('type') == 'money' and (value or value==0):
                    value = "{:,.2f}".format(value)
                if column.get('type')=='round_dollars' and (value or value==0):
                    value = "${:,.0f}".format(value)
                if column.get('type') == 'dollars' and (value or value==0):
                    value = "${:,.2f}".format(value)
                if column.get('type') == 'integer' and (value or value==0):
                    value = "{:,.0f}".format(value)
                elif column.get('type') == 'percent' and value != '':
                    value = "{:,.1f}%".format(value*100)
                elif column.get('type') == 'date' and value:
                    value = format_date(value)
                if target == 'html' and column.get('html'):
                    value = column.html % value
                if target == 'html' and column.get('link'):
                    value = a(value, href=column.link % value, target='_blank')

                # report_link and report_key allows linking into other reports
                if target == 'html' and column.get('report_link') and \
                   not self.params.group_bys and \
                   value and value != 'No':
                    report_link = column['report_link']
                    report_key  = column['report_key']
                    value = a(value, href='%s?%s=%s' % (report_link,
                                                        report_key,
                                                        row[report_key]),
                              target='_blank')
                row2.append(value)
            table.append(list(map(str, row2)))
        if totals:
            return row2
        return table
    
    def getRowCount(self):
        if '_row_count' not in self.__dict__:
            sql = self.sqlBuilder.getCountSQL()
            if self.params.debug_sql:
                self.debug_msg += p("Count SQL: %s" % pretty_sql(sql, True))
            self._row_count = self.db.query(sql)[0]['count']
        return self._row_count

    def getTotals(self, target='html'):
        return self.getData(target, totals=1)

# Helpers

def dict2odict(src_dict):
    '''Return an dict converted recursively into an odict
       Also expand environement vars
    '''
    o = odict()
    for k,v in list(src_dict.items()):
        if isinstance(v, dict):
            o[k] = dict2odict(v)
        elif isinstance(v, list):
            o[k] = []
            for l in v:
                if isinstance(l, dict):
                    o[k].append(dict2odict(l))
                else:
                    o[k].append(l)
        elif isinstance(v, str):
            if '\$' in v: # unescape \$
                v = v.replace('\$', '$')
            elif '$' in v:
                import re
                envvar = re.sub(r'.*\$([^/.]*).*', r'\1', v)
                envvar_val = os.getenv(envvar, 'Uknown_env_var:%s' % envvar)
                v = re.sub('\$[^/.]*', envvar_val, v)
            o[k] = v
        else:
            o[k] = v
    return o
