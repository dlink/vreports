from vweb.htmltable import HtmlTable
from vweb.html import *

class ReportColumnsError(Exception): pass

class ReportColumns(object):

    def __init__(self, params):
        self.params = params

    def getColumn(self, name):
        '''Return a column object for a given name'''
        for c in self.params.columns:
            if c.name == name:
                return c
        raise ReportColumnsError('Column not found: %s' % name)

    def getSelectedColumns(self):
        columns = [c for c in self.params.columns
                   if c.get('selected') and not self.disabled(c)]
        # if nothing selected use first column
        # (the 0th column could be a separator)
        if not columns:
            columns = [self.params.columns[1]]
        return columns

    def disabled(self, column):
        # summary and not a summary column and has not aggregate func
        if self.params.group_bys \
                and column.name not in [c.name for c in self.params.group_bys]\
                and 'aggregate_func' not in column:
            return True
        
        # not summary and column mode is aggregate
        elif not self.params.group_bys and column.get('mode') == 'aggregate':
            return True

        # all else okay
        return False
        
    def getColumnChooser(self):
        title = div(b('Columns'), class_='report-controls-title')
    
        # buttons
        reset_button = a('Reset Columns', id='reset-columns', class_='vbutton',
                         onclick='reset_columns()')
        clear_button = a('Clear Columns', id='clear-columns', class_='vbutton',
                         onclick='clear_columns()')
        report_columns = div(title + \
                              self.getColumnsDescription() + \
                              self.getGuts() + \
                              reset_button + \
                              clear_button,
                              id='column-chooser',
                              class_='report-controls')
        return report_columns
    
        # container:
        #return div(show_button + \
        #           report_controls,
        #           id='column_chooser_container')

    def getColumnsDescription(self):
        return span(self.params.get('columns_description', ''),
                    class_='columnDescription')

    def getGuts(self):
        # Table of column checkboxes NUM_COL's wide
        NUM_COL = 4
        table = HtmlTable(id='column-chooser-table',
                          class_='report-controls-table')
        num_separators = len([c for c in self.params.columns[1:]
                              if c.get('type') == 'separator'])
        num_checkboxes = len(self.params.columns) + num_separators
        remander = num_checkboxes % NUM_COL
        if remander:
            num_rows = (num_checkboxes/NUM_COL)+1
        else:
            num_rows = num_checkboxes/NUM_COL
        rows = [ [] for x in range(num_rows+1)]
        row_num = 0
        
        # checkboxs
        hidden = []
        skip_one = 0
        for i, column in enumerate(self.params.columns):

            if column.get('type') == 'separator':
                checkbox = b(column.display)
                if i != 0:
                    skip_one = 1

            elif self.disabled(column):
                
                # hidden fields
                style = 'color: lightgrey'
                h = input(type='hidden',
                          name='%s_column' % column.name,
                          value=column.get('selected', ''))
                mark = 'x' if column.get('selected') else '&nbsp;'
                display = span('[ %s ] %s' % (mark,column.display),style=style)
                checkbox = display + h
                
            else:
            
                # checkbox
                checkbox_params = {'type': 'checkbox',
                                   'name': '%s_column' % column.name}
                if column.get('selected'):
                    checkbox_params['checked'] = 'checked'
                if column.get('default'):
                    checkbox_params['class'] = 'default_column'
                if column.get('minor'):
                    display = span(column.display, class_='cc_minor')
                else:
                    display = span(column.display, class_='cc_major')
                                 
                checkbox = input(**checkbox_params) + display
            
            # build matrix of checkboxes, n x num_rows
            if skip_one:
                rows[row_num].append('')
                row_num += 1
                if row_num >= num_rows:
                    row_num = 0
                skip_one = 0

            rows[row_num].append(checkbox)
            row_num += 1
            if row_num >= num_rows:
                row_num = 0
                
        # build formated table:        
        for row in rows:
            table.addRow(row)
        table_of_columns = table.getTable()
        return table_of_columns
