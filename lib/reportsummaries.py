from vweb.htmltable import HtmlTable
from vweb.html import *

class ReportSummariesError(Exception): pass

class ReportSummaries(object):
    
    def __init__(self, params):
        self.params = params
        
    def getControls(self):
        title = div(b('Summaries'), class_='report-controls-title')

        # Summaries
        table = HtmlTable(class_='report-controls-table')
        for n in range(1, self.params.num_group_bys+1):
            if n == 1:
                row = ['Summarize by:', self._getGroupByMenu(n)]
            else:
                row = ['', self._getGroupByMenu(n)]
            table.addRow(row)
        table.setColClass(1, 'filter-field')
        table.setColClass(2, 'filter-field')
        summarize_by = div(table.getTable(), id='summarize_by')

        # Show summary totals
        table = HtmlTable(class_='report-controls-table')
        params = {'name': 'show_summary_totals', 'type': 'checkbox'}
        if self.params.show_summary_totals:
            params['checked'] = 1
        checkbox = input(**params)
        table.addRow(['Show Summary Totals', checkbox])
        show_summary_totals = div(table.getTable(), id='show_summary_totals')

        # Rest button
        reset_button = a('Reset Summary', id='reset-filters', class_='vbutton',
                         onclick='reset_summaries()')

        # report control
        input_section = div(summarize_by + show_summary_totals,
                            id='summary-input-section')
        report_controls = div(title + input_section + reset_button,
                              id = 'summary-chooser',
                              class_ ='report-controls')
        return report_controls
        

    def _getGroupByMenu(self, n):
        options = ''
        options += option('No Summary', value='')
        if len(self.params.group_bys) >= n:
            group_by_name = self.params.group_bys[n-1].name
        else:
            group_by_name = None
        for c in sorted(self.params.columns, key=lambda f: f['name']):

            if c.get('group_by'):
                if  c.name == group_by_name:
                    options += option(c.display, value=c.name, selected='1')
                else:
                    options += option(c.display, value=c.name)
        return select(options, name='group_by_%s' % n)
