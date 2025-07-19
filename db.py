import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")

#connect to client
client = MongoClient(mongo_uri)
    
print(client.list_database_names())

db = client[db_name]
characters_collection = db["characters"]
