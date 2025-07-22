import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.errors import ServerSelectionTimeoutError

#Default path to local JSON data:
DEFAULT_JSON_FILE = "characters.json"

client = None
db = None
characters_collection = None

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
        return True
    
    except ServerSelectionTimeoutError:
        print("⚠️ MongoDB not available. Falling back to JSON.")
        if os.path.exists(DEFAULT_JSON_FILE):
            with open(DEFAULT_JSON_FILE, "r") as f:
                characters_data = json.load(f)
        else:
            characters_data = {}
            print("❌ No JSON file found.")
    
def load_characters_fallback():
    if os.path.exists(DEFAULT_JSON_FILE):
        with open(DEFAULT_JSON_FILE, "r") as f:
            return json.load(f)
    else:
        print("❌ No JSON file found.")
        return {}
    
# Call this at startup
db_connected = connect_to_db()

# Then you can access data like this in your app:
if db_connected:
    characters_data = {
        doc["name"]: doc for doc in characters_collection.find()
    }
else:
    characters_data = load_characters_fallback()
    
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
