from vlib.sqlutils import pretty_sql

from vweb.htmltable import HtmlTable
from vweb.html import *

class ReportSqlPanel(object):
    
    def __init__(self, params, sqlBuilder):
        self.params = params
        self.sqlBuilder = sqlBuilder
        
    def getSqlPanel(self):
        hide_button = a('[Hide]', onclick='hide_sql_panel()')

        spacer = div('&nbsp;', class_='floatr')
        
        title = div(b(i('Show SQL')) + '&nbsp;' + hide_button + spacer,
                    id='sql_panel_title')

        table = HtmlTable(id='sql_panel_table')
        table.addRow([b('SQL'), b('Count SQL')])

        count_sql = self.sqlBuilder.getCountSQL()
        count_sql_pretty = div(pretty_sql(count_sql, html=True) + ';')
        
        sql  = self.sqlBuilder.getSQL()
        sql_pretty = div(pretty_sql(sql, html=True) + ';')

        table.addRow([sql_pretty, count_sql_pretty])
        table.setColWidth(1, '50%')
        table.setRowVAlign(2, 'top')
        
        show_sql = div(title + \
                       table.getTable(),
                       id='sql_panel')
        
        return show_sql
