from copy import copy

from vlib.odict import odict

from vweb.html import *

class ReportSqlBuilder(object):
    
    def __init__(self, params, reportColumns):
        self.params        = params
        self.reportColumns = reportColumns
        self.sql_params    = odict(base_table=params.base_table,
                                   base_table_alias=params.base_table_alias)
        self.where_aliases  = []
        self.aliases        = []
        self.prepped = False
        
    def getCountSQL(self):
        self._sqlPrep()
        sql_t = 'select {count_select_clause} ' \
                 'from {base_table} {base_table_alias}' \
                 '{count_join_clause} ' \
                 '{where_clause}'
        sql = sql_t.format(**self.sql_params)
        return sql
    
    def getSQL(self, limited=True):
        self._sqlPrep()
        sql_t = 'select {select_clause} ' \
                'from {base_table} {base_table_alias} ' \
                '{join_clause} ' \
                '{where_clause} ' \
                '{group_by_clause} ' \
                '{order_by_clause} '
        if limited:
            sql_t += \
                '{limit_clause}'
        sql = sql_t.format(**self.sql_params)
        #from vlib.sqlutils import pretty_sql
        #print 'sql: %s' % pretty_sql(sql, True)
        return sql

    def _sqlPrep(self):
        if self.prepped:
            return
        
        # Build self.where_aliases - based on tables needed for where clause
        #   and group_by.aliases   - based on tables needed for group by
        #   and self.aliases       - based on where_aliases, and tables
        #                               need in select clause
        self.where_aliases = self._addAliases('controls', 'filter', 'value',[])
        self.group_by_aliases = self._addAliases('columns','select','group_by',
                                                 self.where_aliases)
        self.aliases  = self._addAliases('columns', 'select', 'selected',
                                         self.where_aliases)
        self.sql_params.select_clause     = self._getSelectClause()
        self.sql_params.count_select_clause = self._getCountSelectClause()
        self.sql_params.join_clause       = self._getJoinClause()
        self.sql_params.count_join_clause = self._getJoinClause('Count')
        self.sql_params.where_clause      = self._getWhereClause()
        self.sql_params.group_by_clause   = self._getGroupByClause()
        self.sql_params.order_by_clause   = self._getOrderByClause()
        self.sql_params.limit_clause      = self._getLimitClause()
        self.prepped = True
        
    def _addAliases(self, driver, sql_field, check_field, existing_list):
        '''Given:
             A  'driver'      either 'controls', or 'columns',
             An 'sql_field'   field to inspect for table aliases,
             A  'check_field' to check for existance, and
             An 'existing_list' of aliases, so as not to repeat
             
           Return a list of table aliases
        '''

        # spec. handling from group_by
        if check_field == 'group_by':
            group_by = self.params.get('group_by')
            if not group_by:
                return []
            
        alias_list = copy(existing_list)
        for data in self.params[driver]:
            # check if column or control is selected
            if not data.get(check_field):
                continue
            # if column, check if not disabled
            if driver == 'columns' and self.reportColumns.disabled(data):
                continue

            # spec. handling for group_by:
            if check_field == 'group_by' and group_by.name != data.name:
                continue
            
            if 'aliases' in data:
                aliases = data.aliases.split(',')
            else:
                aliases = _getAliases(data[sql_field])

            for alias in aliases:
                if alias==self.params.base_table_alias or alias in alias_list:
                    continue
                
                # validate
                self._validateAlias(alias)
                # check dependencies
                require = self.params.table_joins[alias].get('require')
                if require and require not in alias_list:
                    # works for two levels
                    require2 = self.params.table_joins[require].get('require')
                    if require2 and require2 not in alias_list:
                        # works for three levels deep only.
                        # TODO: make recurisve
                        require3 = self.params.table_joins[require2].get('require')
                        if require3 and require3 not in alias_list:
                            alias_list.append(require3)
                        alias_list.append(require2)
                    alias_list.append(require)
                # add alias
                alias_list.append(alias)
                
        return alias_list
    
    def _validateAlias(self, alias):
        '''Verify that alias is defined in table_joins'''
        if alias not in self.params.table_joins:
            emsg = "Table alias '%s' undefined in table_joins" % alias
            raise Exception(emsg)
        
    def _getSelectClause(self):
        select = []
        for c in self.reportColumns.getSelectedColumns():
            if self.params.get('group_by') and c.get('aggregate_func'):
                s = "%s(%s)" % (c.aggregate_func, c.select)
            else:
                s = c.select
            select.append("%s as %s" % (s, c.name))
        return ', '.join(select)

    def _getCountSelectClause(self):
        if 'group_by' in self.params:
            return 'count(distinct %s) as count' % self.params.group_by.select
        else:
            return 'count(*) as count'
        
    def _getSelectClause0(self):
        return ', '.join(["%s as %s" % (c.select, c.name) \
                          for c in self.reportColumns.getSelectedColumns()])
    
    def _getJoinClause(self, target=''):
        '''Return SQL Join Statement
           based on (self.aliases or self.where_aliases) and
                    self.params.table_joins
           target param in (''|'Count')
        '''
        aliases = self.group_by_aliases or self.where_aliases \
                  if target == 'Count' else self.aliases
        joins = []
        for alias in aliases:
            join = self.params.table_joins[alias].clause
            joins.append(join)
        if not joins:
            return ''
        return '\n' + '\n'.join(joins)

    def _getWhereClause(self):
        filters = []
        for control in self.params.controls:
            if control.value: 
                value = control.value
                if isinstance(value, (str, unicode)):
                    value = value.replace("'", "''")
                filters.append(control.filter.format(value=value))
        if not filters:
            return ''
        return 'where ' + ' and '.join(filters)

    def _getGroupByClause(self):
        if 'group_by' in self.params:
            return 'group by %s' % self.params.group_by.select
        return ''
                          
    def _getOrderByClause(self):
        if self.params.get('group_by'):
            sort_column    = self.params.s_sort_column
            sort_direction = self.params.s_sort_direction
        else:
            sort_column    = self.params.sort_column
            sort_direction = self.params.sort_direction
        return 'order by %s %s' % (sort_column, sort_direction)
    
    def _getLimitClause(self):
        return 'limit {limit} offset {offset}'.format(
            limit=self.params.display_num_rows,
            offset=(self.params.page_num-1) * self.params.display_num_rows)
    
def _getAliases(sql_code):
    '''Find table aliases from sql code frag
       Else throw Exception

       eq.: a.status_id = 2   # <== returns ['a']
    '''
    try:
        alias = sql_code[0:sql_code.index('.')]
        # accept only alpha-numeric and '_':
        if not alias.replace('_','').isalnum():
            raise Exception('Alias not Alphanumeric')
    except Exception, e:
        raise Exception("Unable to determine table alias from sql_code: '%s'. You must specify an 'alias' value. %s" % (sql_code, e))
    return [alias]
        