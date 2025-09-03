import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ServerSelectionTimeoutError
from character_store import CharacterStore

# Default path to local JSON data:
DEFAULT_JSON_FILE = "characters.json"

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
        characters_collection = db["characters"]
        items_collection = db["newItems"]
        cyberware_items = db["gameItems"]
        print("✅ Connected to MongoDB.")
        return {
            "characters": characters_collection,
            "items": items_collection,
            "cyberware_items": cyberware_items,
        }

    except ServerSelectionTimeoutError:
        print("⚠️ MongoDB not available. Falling back to JSON.")
        return None


def load_characters_fallback():
    if os.path.exists(DEFAULT_JSON_FILE):
        with open(DEFAULT_JSON_FILE, "r") as f:
            return json.load(f)
    else:
        print("❌ No JSON file found.")
        return {}


# Init once at import
collections = connect_to_db()


def get_data_stores():
    collections = connect_to_db()
    if collections:
        return {
            "character_store": CharacterStore(),
            "items_collection": collections["items"],
            "cyberware_items": collections["cyberware_items"],
        }
    else:
        fallback_data = load_characters_fallback()
        return {
            "character_store": CharacterStore(),
            "items_collection": None,
            "cyberware_items": None,
        }
