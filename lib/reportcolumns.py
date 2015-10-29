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
        return [c for c in self.params.columns
                if c.get('selected') and not self.disabled(c)]
    
    def disabled(self, column):
        group_by = self.params.get('group_by')
        if group_by \
               and column.name != group_by.name \
               and 'aggregate_func' not in column:
            return True
        elif not group_by and column.get('mode') == 'aggregate':
            return True
        else:
            return False
        
    def getColumnChooser(self):

        hide_button = a('[Hide]', onclick='hide_column_chooser()')

        spacer = div('&nbsp;', class_='floatr')                  

        title = div(b(i('Column Chooser')) + '&nbsp;' \
                    + hide_button + spacer,
                    id='column_chooser_title')
    
        # buttons
        reset_button = input(name='reset', value='Reset Defaults',
                             type='button',onclick='reset_column_defaults()')
        
        other_buttons = p(' &nbsp; '.join([reset_button]))
        
        report_columns = div(title + \
                              self.getColumnsDescription() + \
                              self.getGuts() + \
                              other_buttons,
                              id='column_chooser')
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
        NUM_COL = 6
        table = HtmlTable(id='column_chooser_table')
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
                                   'name': '%s_column' % column.name,
                                   'onchange': 'submit()'}
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
    
    def getShowButton(self):
        #show_button = a('[Column Chooser]',
        #                id='column_chooser_show',
        #                onclick='show_column_chooser()')
        show_button = input(name='column_chooser', value='Choose Columns', type='button',
                            id='column_chooser_show',
                            onclick='show_column_chooser()')
        return show_button
