from typing import List, Dict


class Table:
    """
    Table object that wraps pyhive.Cursor.execute() and pyhive.Cursor.()
    How to use:
    Example:
        Table(cursor=<cursor>, table=<table_name>).select(filters={<field_name>: <event_id>}, limit=<hive_limit>)

        Select query will be generated:
        SELECT * FROM <table_name> WHERE <field_name> = <event_id> LIMIT <hive_limit>

        And execute
    """
    def __init__(self, cursor, table: str):
        """
        Construct class 'Table'
        :param cursor: return Connector.create() object
        :param table: Table name
        """
        if cursor is None:
            raise ValueError('Cursor should be provided to database')
        self.table = table
        self._cursor = cursor

    @staticmethod
    def prepare_projection(fields: List[str]):
        projection = str()
        if fields:
            if not isinstance(fields, list):
                raise TypeError(f"{fields} must be a list")
            if not all(isinstance(field, str) for field in fields):
                raise TypeError(f"each element in {fields} must be a string")
            projection = " ,".join(fields)
        else:
            projection += "*"
        return projection

    @staticmethod
    def prepare_conditions(filters: Dict[str, str]) -> str:
        if not filters:
            return str()
        if not (isinstance(filters, dict)):
            raise TypeError(f"{filters} must be a dict")
        for key, value in filters.items():
            if not isinstance(key, str):
                raise TypeError(f"{key} in {filters} must be a string")
        conditions = " WHERE " + " AND ".join(f"{field} = {value}" for field, value in filters.items())
        return conditions

    def prepare_select(self, fields: List[str], filters: Dict[str, str], limit: str):
        projections = self.prepare_projection(fields)
        conditions = self.prepare_conditions(filters)
        query_string = f"SELECT {projections} FROM {self.table}{conditions}"
        if limit and isinstance(limit, int):
            query_string += f" LIMIT {limit}"
        return query_string

    def select(self, fields: List[str]=None, filters: Dict[str, str]=None, limit: str=None):
        """
        Forms the SQL query statement string

        :param: fields: fields for select
        :return: self
        """
        query_string = self.prepare_select(fields, filters, limit)
        self.execute(query_string)
        return self

    def execute(self, request: str):
        """
        Executes request

        :param: query string
        :return: Object from table. View {'field_name': 'field_value'}
        """
        cursor = self._cursor
        cursor.execute(request)
        data = cursor.fetchall()
        column_names = (field[0].split('.')[1] for field in cursor.description)
        return dict(zip(column_names, *data))
