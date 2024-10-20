#!/usr/bin/env python



import re
import os
import sys

from vlib import db
from vlib.datatable import DataTable
from vlib.utils import pretty

class GeneratorError(Exception): pass

class Generator(object): 

    def __init__(self):
        self.db = db.getInstance()

    def genYaml(self, tablename, alias):
        '''Given a tablename and an given alias
           Read table schema info from the database
           Return vreports Column yaml file
        '''

        # Todo add count column to output:
        """
        - name    : count
          select  : '*'
          aliases : c
          mode    : aggregate
          aggregate_func: count
          type    : integer
          default : true
        """

        # Read columns info from database
        dt = DataTable(self.db, tablename)
        columns = []
        for row in dt.describe():
            name = row['Field']
            db_type = row['Type']

            # Convert DB types to vreports Types:

            # remove numbers from db_type
            db_type = re.sub(r'[0-9]', r'', db_type)

            # care not about unsigned:
            db_type = db_type.replace(' unsigned', '')

            if db_type in ('int()', 'tinyint()', 'smallint()', 'bigint()',
                           # mssql
                           'bit', 'int', 'bigint'):
                type = 'integer'
            elif db_type in ('char()', 'varchar()','text', 'nvarchar') or 'enum' in db_type:
                type = 'string'
            elif db_type in ('datetime', 'timestamp'):
                type = 'datetime'
            elif db_type in ('date',):
                type = 'date'
            elif db_type in ('decimal(,)', 'float'):
                type = 'money'
            else:
                raise GeneratorError('Unrecognized db_type: %s' % db_type)
            columns.append({'name': name, 'type': type})

        # Create Yaml by hand
        #   not using yaml.dump for more control
        o = 'columns:\n\n'
        for i, c in enumerate(columns):
            o += '   - name   : %s\n' % c['name']
            o += '     select : %s.%s\n' % (alias, c['name'])
            o += '     type   : %s\n' % c['type']
            if c['type'] == 'money':
                o += '     aggregate_func: sum\n'
            o += '     default: true\n'
            o += '\n'

        o += '''
   # count

   - name    : count
     select  : '*'
     aliases : %s
     mode    : aggregate
     aggregate_func: count
     type    : integer
     default : true''' % alias

        return o

def syntax():
    progname = os.path.basename(sys.argv[0])
    print("%s <table_name> <table_alias>" % progname)
    print()
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        syntax()

    table_name  = sys.argv[1]
    table_alias = sys.argv[2]

    g=Generator()
    print(g.genYaml(table_name, table_alias))
