import json
import os


class CharacterStore:
    def __init__(self, db=None, fallback_file=None):
        self.db = db
        self.use_db = db is not None
        self.fallback_file = fallback_file

        if not self.use_db:
            self._ensure_file()
            print("Opening JSON...")
            with open(self.fallback_file, "r") as f:
                self.data = json.load(f)

    def _ensure_file(self):
        if not os.path.exists(self.fallback_file):
            print("❌ No JSON file found. Creating...")
            with open(self.fallback_file, "w") as f:
                json.dump({}, f, indent=4)

    def find(self):
        if self.use_db:
            return self.db.find()
        return self.data.values()

    def find_one(self, query):
        if self.use_db:
            return self.db.find_one(query)

        key = query.get("_id") or query.get("name")
        if key in self.data:
            return self.data[key]

        for char in self.data.values():
            if all(char.get(k) == v for k, v in query.items()):
                return char
        return None

    def insert_one(self, doc):
        if self.use_db:
            return self.db.insert_one(doc)

        self.data[doc["_id"]] = doc
        self._write_data()

    def update_one(self, query, update, upsert=False):
        if self.use_db:
            return self.db.update_one(query, update, upsert=upsert)

        _id = query.get("_id")
        if _id in self.data:
            self.data[_id].update(update.get("$set", {}))
        elif upsert:
            self.data[_id] = update.get("$set", {})
        self._write_data()

    def delete_one(self, query):
        if self.use_db:
            return self.db.delete_one(query)

        key = query.get("_id") or query.get("name")
        if key and key in self.data:
            del self.data[key]
            self._write_data()
            return True
        return False

    def _write_data(self):
        with open(self.fallback_file, "w") as f:
            json.dump(self.data, f, indent=4)
