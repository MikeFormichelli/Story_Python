import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ServerSelectionTimeoutError
import sqlite3
from .character_store import CharacterStore
from .SQLiteCollection import SQLiteCollectionWrapper

print(os.path.realpath(__file__))
# Default path to local JSON data:
DEFAULT_JSON_FILE = "data/characters.json"
DEFAULT_SQLITE_FILE = "data/cyberpunk.db"

# globals:
client = None
db = None
characters_collection = None
character_store = None  # <_-centralized store instance

# load environment
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")


def connect_to_db():
    global client, db, characters_collection
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")  # quick connectivity check
        db = client[db_name]
        collection_names = db.list_collection_names()

        return_dict = {}
        for cn in collection_names:
            return_dict[cn] = db[cn]

        print("✅ Connected to MongoDB.")
        return return_dict

    except ServerSelectionTimeoutError:
        print("⚠️ MongoDB not available. Falling back to JSON.")
        return None


def get_data_stores():
    collections = connect_to_db()
    col_dict = {
        "character_store": None,
        "items_store": None,
    }

    if collections:
        # MongoDB available ✅
        for k, v in collections.items():
            col_dict[k] = v

        # re-init CharacterStore with MongoDB collection
        if "characters" in collections:
            col_dict["character_store"] = CharacterStore(collections["characters"])

    else:
        col_dict["character_store"] = CharacterStore(fallback_file=DEFAULT_JSON_FILE)

    if not collections:
        sqlite_conn = connect_to_sqlite()
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        sqlite_tables = [t[0] for t in cursor.fetchall()]

        item_store = {}
        for tname in sqlite_tables:

            item_store[tname] = SQLiteCollectionWrapper(sqlite_conn, tname)
            # data = list(cursor.execute(f"SELECT * FROM {tname}"))
            # col_names = [description[0] for description in cursor.description]
            # data_list = []
            # for item in data:
            #     item_dict = {}
            #     for i in range(len(col_names)):
            #         item_dict[col_names[i]] = item[i]
            #     data_list.append(item_dict)
            # items_store[tname] = data_list

        col_dict["items_store"] = item_store

    return col_dict


def connect_to_sqlite():
    try:
        conn = sqlite3.connect(DEFAULT_SQLITE_FILE)

        print("✅ Connected to SQLite (fallback db)")

        return conn

    except sqlite3.Error as e:
        print(f"💥 SQLITE connection failed: {e}")
        return None
