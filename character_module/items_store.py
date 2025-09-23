import json


class ItemsStore:
    def __init__(self, db=None, sqlite_conn=None):
        self.db = db
        self.sqlite_conn = sqlite_conn
        self.use_mongo = db is not None
        self.use_sqlite = sqlite_conn is not None

    def find(self):
        if self.use_mongo:
            return list(self.db.find())
        elif self.use_sqlite:
            cursor = self.sqlite_conn.cursor()
            cursor.execute("SELECT id, name, type, attributes FROM items")
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "type": r[2],
                    "attributes": json.loads(r[3] or "{}"),
                }
                for r in rows
            ]
        return []

    def insert_one(self, item):
        if self.use_mongo:
            return self.db.insert_one(item)
        elif self.use_sqlite:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO items (id, name, type, attributes) VALUES (?, ?, ?, ?)",
                (
                    item["id"],
                    item["name"],
                    item["type"],
                    json.dumps(item.get("attributes", {})),
                ),
            )
            self.sqlite_conn.commit()
