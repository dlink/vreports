from unittest import TestCase
from unittest.mock import Mock

from vlib.odict import odict

from reportbase import ReportBase
from reportcolumns import ReportColumns
from reportsqlbuilder import ReportSqlBuilder

class TestLinkSelect(TestCase):
    def test_adds_hidden_link_to_select_clause(self):
        column = odict({'name': 'bid', 'select': 'p.bid', 'selected': True,
                        'link_select': "concat(s.admin_url, '/', p.bid)"})
        params = odict({'base_table': 'products', 'base_table_alias': 'p',
                        'columns': [column], 'group_bys': []})
        builder = ReportSqlBuilder(params, ReportColumns(params))

        self.assertEqual(
            builder._getSelectClause(),
            "p.bid as bid, concat(s.admin_url, '/', p.bid) as bid__link")

    def test_uses_selected_link_for_html(self):
        column = odict({'name': 'bid', 'selected': True,
                        'link_select': 's.admin_url'})
        report = ReportBase.__new__(ReportBase)
        report.params = odict({'debug_sql': False})
        report.sqlBuilder = Mock()
        report.sqlBuilder.getSQL.return_value = 'select ...'
        report.reportColumns = Mock()
        report.reportColumns.getSelectedColumns.return_value = [column]
        report.db = Mock()
        report.db.query.return_value = [
            {'bid': 325, 'bid__link': 'https://example.com/products/325'}]

        table = report.getData()

        self.assertIn('href="https://example.com/products/325"', table[0][0])
        self.assertIn('>325</a>', table[0][0])

    def test_does_not_require_selected_link_for_totals(self):
        column = odict({'name': 'bid', 'selected': True,
                        'link_select': 's.admin_url'})
        report = ReportBase.__new__(ReportBase)
        report.params = odict({'debug_sql': False})
        report.sqlBuilder = Mock()
        report.sqlBuilder.getTotalsSQL.return_value = 'select totals ...'
        report.reportColumns = Mock()
        report.reportColumns.getSelectedColumns.return_value = [column]
        report.db = Mock()
        report.db.query.return_value = [{'bid': ''}]

        self.assertEqual(report.getData(totals=True), [''])
