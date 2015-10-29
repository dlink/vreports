from vweb.htmltable import HtmlTable
from vweb.html import *

class ReportControlsError(Exception): pass

class ReportControls(object):
    
    def __init__(self, params):
        self.params = params
        

    def getShowButton(self):
        #show_button = a('[Controls]',
        #                id='report_controls_show',
        #                onclick='show_report_controls()')
        show_button = input(name='controls', value='Filters', type='button',
                            id='report_controls_show',
                            onclick='show_report_controls()')
        return show_button

    def getControl(self, name):
        '''Return a control object for a given name'''
        for c in self.params.controls:
            if c.name == name:
                return c
        raise ReportControlsError('Control not found: %s' % name)

    def getControls(self):
        hide_button = a('[Hide]', onclick='hide_report_controls()')

        spacer = div('&nbsp;', class_='floatr')
        
        title = div(b(i('Report Controls')) + '&nbsp;' + hide_button + spacer,
                    id='report_controls_title')

        table = HtmlTable(id='report_controls_table')
        cwidgets = ''
        filters = []
        for control in self.params.controls:
            ctitle = control.display
            if control.type in ('string', 'date'):
                cinput = self._getInput(control)
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

        # group_by
        table.addRow([hr(), hr()])
        table.addRow(['Summarize by:', self._getGroupByMenu()])
        table.setCellColSpan(table.rownum, 2, 2)

        clear_button = input(name='clear_button', value='Clear All',
                             type='button', onclick='clear_controls()')
            
        report_controls = div(title + \
                              table.getTable() + \
                              clear_button,
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
                       value=control.get('value', ''),
                       onChange='submit()')
        return cinput

    def _getCheckbox(self, control):
        params = {'name' : control.name,
                  'class': control.type,
                  'type' : 'checkbox',
                  'value': 'True',
                  'onChange': 'submit()'}
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
        return select(options, name=control.name, onChange='submit()')

    def _getGroupByMenu(self):
        options = ''
        options += option('No Summary', value='')
        group_by = self.params.get('group_by')
        group_by_name = group_by.name if group_by else None
        for c in self.params.columns:
            if c.get('group_by'):
                if  c.name == group_by_name:
                    options += option(c.display, value=c.name, selected='1')
                else:
                    options += option(c.display, value=c.name)
        return select(options, name='group_by', onChange='submit()')

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
    NUM_COL = 5
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
