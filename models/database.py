import os
from sqlalchemy import MetaData, text, create_engine, inspect


class Database:
    _instance = None 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.engine = None
        self.connection = None
        self.db_type= 'mysql'
    def connect(self):
        if self.connection:
            return

        connection_string = self._get_sql_connection_string()
        self.engine = create_engine(connection_string)
        self.connection = self.engine.connect()

        if not self.connection:
            raise ValueError("Failed to establish database connection.")

    def _get_sql_connection_string(self):
        user = os.environ.get(f"{self.db_type.upper()}_USER", "")
        password = os.environ.get(f"{self.db_type.upper()}_PASSWORD", "")
        host = os.environ.get(f"{self.db_type.upper()}_HOST", "")
        port = os.environ.get(f"{self.db_type.upper()}_PORT", "")
        dbname = os.environ.get(f"{self.db_type.upper()}_DBNAME", "")

        if self.db_type == "mysql":
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"

    def get_tables(self):
        if not self.connection:
            self.connect()

        try:
            return inspect(self.engine).get_table_names()
        except Exception as e:
            raise ValueError(f"Error fetching table names: {str(e)}")

    def get_fields(self, table_name):
        if not self.connection:
            self.connect()

        try:

            columns = inspect(self.engine).get_columns(table_name)
            return [column['name'] for column in columns]

        except Exception as e:
            raise ValueError(f"Error fetching fields for table {table_name}: {str(e)}")

    def query(self, table_name, field=None, target_query=None):
        try:
          
            return self._query_real_data(table_name, field, target_query)
        except Exception as e:
            raise ValueError(f"Error querying data for table {table_name}: {str(e)}")

    def _query_real_data(self, table_name, field=None, target_query=None):
        if not self.connection:
            self.connect()
        if self.db_type:
            return self._query_sql_data(table_name, field, target_query)
       
        return []

    def _query_sql_data(self, table_name=None, field=None, targeted_query=None):
        metadata = MetaData()
        print(targeted_query)

        if targeted_query:
            with self.engine.connect() as connection:
                result_proxy = connection.execute(text(targeted_query))
                columns = result_proxy.keys()
                result = result_proxy.fetchall()
        else:
            metadata.reflect(only=[table_name], bind=self.engine)
            table = metadata.tables[table_name]

            if field:
                query = table.select().with_only_columns([table.c[field]])
                columns = field
            else:
                query = table.select()
                columns = table.columns.keys()

            with self.engine.connect() as connection:
                result = connection.execute(query).fetchall()

        rows = []
        for row in result:
            row_data = {}
            for column, value in zip(columns, row):
                row_data[column] = value
            rows.append(row_data)

        return rows
