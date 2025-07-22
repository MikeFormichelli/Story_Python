import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ServerSelectionTimeoutError
from character_store import CharacterStore

#Default path to local JSON data:
DEFAULT_JSON_FILE = "characters.json"

#globals:
client = None
db = None
characters_collection = None
character_store = None # <_-centralized store instance

#load environment
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")

def connect_to_db():
    global client, db, characters_collection
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.admin.command("ping") #quick connectivity check
        db = client[db_name]
        characters_collection = db["characters"]
        print("✅ Connected to MongoDB.")
        return characters_collection
    
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
collection = connect_to_db()

# Then you can access data like this in your app:
if collection is not None:
    character_store = CharacterStore(db=collection)
else:
    print("⚠️ Error fetching data from MongoDB. Falling back to JSON.")
    fallback_data = load_characters_fallback()
    character_store = CharacterStore()
    
# #connect to client
# client = MongoClient(mongo_uri)
    
# print(client.list_database_names())

# db = client[db_name]
# characters_collection = db["characters"]


# try:
#     # This forces a connection attempt
#     client.server_info()
# except ServerSelectionTimeoutError:
#     print("❌ MongoDB is not running or cannot be reached.")
#     exit(1)
