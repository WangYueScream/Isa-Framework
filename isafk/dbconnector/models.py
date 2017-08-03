from .conditions import BaseCondiction
from .joins import BaseJoin


class Model:
    def __init__(self, table, field, db_conn):
        self.table = table
        self.field = field
        self.db = db_conn

    def search(self, fields=None, condition=None, order: dict=None, group=None, limit=None):
        sql = '''SELECT {fields} FROM `{table}`'''.format(fields='*' if not fields else ", ".join(fields), table=self.table)
        if condition:
            if not isinstance(condition, BaseJoin) and not isinstance(condition, BaseCondiction):
                raise TypeError('Must Be Condition Class')
            sql += ' WHERE ' + condition.format()

        if group:
            fields = ", ".join(group)
            statement = ' GROUP BY {fields}'.format(fields=fields)
            sql += statement

        if order:
            field = ", ".join(order['fields'])
            sort = order.get('sort', 'ASC')

            statement = " ORDER BY {field} {sort}".format(field=field, sort=sort)
            sql += statement

        if limit:
            limit = [ str(ele) for ele in limit]
            statement = " LIMIT " + ", ".join(limit)
            sql += statement

        return self.db.execute(sql)

    def update(self, conditions: BaseCondiction or BaseJoin, **options):
        if not isinstance(conditions, BaseCondiction) and not isinstance(conditions, BaseJoin):
            raise TypeError('Must Be Condition Class')


        values = []
        for k, v in options.items():
            v = '"%s"' % v if isinstance(v, str) else v
            values.append('{key} = {value}'.format(key=k, value=v))


        sql = 'UPDATE {table} SET {values} WHERE {conditions}'.format(table=self.table, values=", ".join(values), conditions=conditions.format())

        return self.db.execute(sql)
    
    def delete(self, conditions: BaseCondiction or BaseJoin):
        if not isinstance(conditions, BaseCondiction) and not isinstance(conditions, BaseJoin):
            raise TypeError('Must Be Condition Class')
        
        statement = '''DELETE FROM {table} WHERE {conditions}'''.format(table=self.table, conditions=conditions.format())
        
        return self.db.execute(statement)

    def add(self, **options):
        key_tmp = []
        value_tmp = []

        for key, value in options.items():
            key_tmp.append(key)
            value_tmp.append(str(value) if isinstance(value, int) else '"%s"' % value)
            
        statement = '''INSERT INTO {table}({key_tmp}) VALUES({value_tmp})'''.format(
            table=self.table,
            key_tmp=", ".join(key_tmp),
            value_tmp=", ".join(value_tmp)
        )
        
        return self.db.execute(statement)