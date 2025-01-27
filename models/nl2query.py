class NL2Query:
    def __init__(self, database, llm_generator):
        self.database = database
        self.llm = llm_generator

    def understand_query(self, query):
        tables = self.database.get_tables()
        target_table = self.llm.get_table_based_on_query(tables, query)
        target_field = None

        print(target_table)
        all_fields = []

        try:
            for table in target_table:
                fields = self.database.get_fields(table)
                all_fields.append(fields)
        except Exception as e:
            print(f"error: {str(e)}")

        target_field = self.llm.get_column_based_on_query(fields, query)
        target_query = self.llm.generate_query_by_llm(tables, all_fields, query)
        return target_table, target_field, target_query