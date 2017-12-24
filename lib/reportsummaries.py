from vweb.htmltable import HtmlTable
from vweb.html import *

class ReportSummariesError(Exception): pass

class ReportSummaries(object):
    
    def __init__(self, params):
        self.params = params
        
    def getControls(self):
        title = div(b('Summaries'), class_='report-controls-title')

        table = HtmlTable(class_='report-controls-table')
        table.addRow(['Summarize by:', self._getGroupByMenu()])

        reset_button = a('Reset Summary', id='reset-filters', class_='vbutton',
                         onclick='reset_summaries()')
            
        table.setColClass(1, 'filter-field')
        table.setColClass(2, 'filter-field')

        report_controls = div(title + \
                              table.getTable() + \
                              reset_button,
                              id = 'summary-chooser',
                              class_ ='report-controls')
        return report_controls
        
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
        return select(options, name='group_by')
