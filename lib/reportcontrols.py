from vweb.htmltable import HtmlTable
from vweb.html import *

class ReportControlsError(Exception): pass

class ReportControls(object):
    
    def __init__(self, params):
        self.params = params
        
    def getControl(self, name):
        '''Return a control object for a given name'''
        for c in self.params.controls:
            if c.name == name:
                return c
        raise ReportControlsError('Control not found: %s' % name)

    def getControls(self):
        title = div(b('Filters'),
                    id='report_controls_title')

        table = HtmlTable(id='report_controls_table')
        cwidgets = ''
        filters = []
        for control in self.params.controls:
            ctitle = control.display
            if control.type in ('string', 'date', 'multiple'):
                cinput = self._getInput(control)
                if control.type == 'multiple':
                    ctitle += ' (multiple - space separated)'
            elif control.type == 'checkbox':
                cinput = self._getCheckbox(control)
            elif control.type == 'menu':
                cinput = self._getControlMenu(control)
            elif control.type == 'no_op':
                ctitle = ''
                cinput = ''
            else:
                raise Exception("ReportControls: Unrecognized control.type: "
                                "%s" % (control.type))
            filters.append([ctitle, cinput])

        for filter in listToTable(filters):
            table.addRow(filter)

        # group_bys
        table.addRow([hr(), hr(), hr(), hr(), hr(), hr()])
        table.setRowClass(table.rownum, 'filter-cell-separator')

        table.addRow([span(b('Summaries'), id='summaries-title')])
        table.setCellColSpan(table.rownum, 1, 3)

        for n in range(1, self.params.num_group_bys+1):
            if n == 1:
                row = ['Summarize by:', self._getGroupByMenu(n)]
            else:
                row = ['', self._getGroupByMenu(n)]
            table.addRow(row)
            table.setRowClass(table.rownum, 'filter-summarize-by')
            table.setCellColSpan(table.rownum, 2, 2)

        reset_button = a('Reset Filters', id='reset-filters', class_='vbutton',
                         onclick='reset_filters()')
            
        table.setColClass(2, 'filter-field')
        table.setColClass(4, 'filter-field')

        report_controls = div(title + \
                              table.getTable() + \
                              reset_button,
                              id='report_controls')
        return report_controls
        # container:
        #return div(#show_button + \
        #           report_controls,
        #           id='report_controls_container')
        
    def _getInput(self, control):
        cinput = input(name=control.name,
                       class_=control.type,
                       type_='text',
                       value=control.get('value', ''))
        return cinput

    def _getCheckbox(self, control):
        params = {'name' : control.name,
                  'class': control.type,
                  'type' : 'checkbox',
                  'value': 'True'}
        if control.get('value'):
            params['checked'] = 1
        cinput = input(**params)
        return cinput

    def _getControlMenu(self, control):
        options = ''
        # sort by menu name
        keys = sorted(control.menu.keys(), key=lambda k: control.menu[k])
        # put 'All' (key = 0) back at the top of the list
        p = keys.index(0)
        keys = [0] + keys[0:p] + keys[p+1:]
        for key in keys:
            #if int(key) == int(control.get('value')):
            if key == control.get('value'):
                options += option(control.menu[key], value=key, selected='1')
            else:
                options += option(control.menu[key], value=key)
        return select(options, name=control.name)

    def _getGroupByMenu(self, n):
        options = ''
        options += option('No Summary', value='')
        if len(self.params.group_bys) >= n:
            group_by_name = self.params.group_bys[n-1].name
        else:
            group_by_name = None
        for c in self.params.columns:
            if c.get('group_by'):
                if  c.name == group_by_name:
                    options += option(c.display, value=c.name, selected='1')
                else:
                    options += option(c.display, value=c.name)
        return select(options, name='group_by_%s' % n)

def listToTable(alist):
    '''Given a list of tuples
       Return a table of N Columns as a list of tuples

       [ a,b           [ a,b,G,H,
         c,d   -->       c,d,I,J,
         e,f             e,f,K,L ]
         G,H
         I,J
         K,L ]
    '''
    NUM_COL = 2
    num_elements = len(alist)
    remander     = num_elements % NUM_COL
    num_rows     = num_elements / NUM_COL
    row_num = 0

    rows = [ [] for x in range(num_rows+1)]
    i = 0
    for el in alist:
        i += 1
        rows[row_num].extend(el)
        row_num += 1
        if (row_num >= num_rows and not remander) or row_num > num_rows:
            if row_num > num_rows:
                remander -= 1
            row_num = 0
    return rows
