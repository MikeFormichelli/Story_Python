class SQLiteCollectionWrapper:
    def __init__(self, conn, table_name):
        self.conn = conn
        self.table = table_name
        self.cursor = self.conn.cursor()

    def find(self, query=None):
        self.cursor.execute(f"SELECT * FROM {self.table}")
        col_names = [desc[0] for desc in self.cursor.description]
        results = []
        for row in self.cursor.fetchall():
            row_dict = {col_names[i]: row[i] for i in range(len(col_names))}
            if query:
                if all(row_dict.get(k) == v for k, v in query.items()):
                    results.append(row_dict)
            else:
                results.append(row_dict)
        return results

    def find_one(self, query=None):
        results = self.find(query)
        return results[0] if results else None
