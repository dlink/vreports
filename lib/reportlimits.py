from vweb.htmltable import HtmlTable
from vweb.html import a, b, div, option, select

class ReportLimitsError(Exception): pass

class ReportLimits(object):
     
    def __init__(self, params):
        self.params = params
        
    def getControls(self):
        title = div(b('Rows to Show'), class_='report-controls-title')

        table = HtmlTable(class_='report-controls-table')
        row = ['Rows to Show:', self._getLimitsMenu()]
        table.addRow(row)

        table.setColClass(1, 'filter-field')
        table.setColClass(2, 'filter-field')

        report_controls = div(title + \
                              table.getTable(),
                              id = 'limit-chooser',
                              class_ ='report-controls')
        return report_controls        

    def _getLimitsMenu(self):
        self.params.limit = self.params.display_num_rows
        options = ''
        for n in (10, 50, 100, 500, 1000):
            if n == self.params.limit:
                options += option(n, value=n, selected=1)
            else:
                options += option(n, value=n)
        return select(options, name='limit')
