from datetime import datetime, timezone
import uuid
import json
from bson import ObjectId

class Character:
    def __init__(self, store, data=None):
        self.store = store
        self._id = str(uuid.uuid4())
        self.image_path = ""
        self.name = ""
        self.handle = ""
        self.sex = ""
        self.age = ""
        self.role = ""
        self.description = ""
        self.experience_level = "Novice"
        self.major_skills = []
        self.minor_skills = []
        self.cyberware = []
        self.relationships = []
        self.last_updated = datetime.now(timezone.utc).isoformat() + "Z"

        if data:
            self._id = data.get("_id", self._id) #preserve original _id if reloaded
            self.load_from_dict(data)

    def load_from_dict(self, data):
        for k, v in data.items():
            setattr(self, k, v)

    def to_dict(self):
        return {
            "_id": self._id,
            "image_path": self.image_path,
            "name": self.name,
            "handle": self.handle,
            "sex": self.sex,
            "age": self.age,
            "role": self.role,
            "description": self.description,
            "experience_level": self.experience_level,
            "major_skills": self.major_skills,
            "minor_skills": self.minor_skills,
            "cyberware": self.cyberware,
            "relationships": self.relationships,
            "last_updated": self.last_updated,
        }
    
    def save_to_store(self):
        self.last_updated = datetime.now(timezone.utc).isoformat() + "Z"
        self.store.update_one({"_id": self._id}, {"$set": self.to_dict()}, upsert=True)

    def delete_from_store(self):
        self.store.delete_one({"_id": self._id})
        
    @staticmethod
    def sync_bi_directional(store, file="characters.json"):
        #load JSON
        try:
            
            with open(file, "r") as f:
                json_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            json_data={}
            
        #load MongoDB Data
        mongo_data = {str(char["_id"]): char for char in store.find()}
        
        #merge keys from both sides
        all_ids = set(json_data.keys()) | set(mongo_data.keys())
        
        merged_data = {}
        
        for _id in all_ids:
            json_char = json_data.get(_id)
            mongo_char = mongo_data.get(_id)
            
            if json_char and mongo_char:
                #both exist, compare timestamps
                json_time = json_char.get("last_updated", "")
                mongo_time = mongo_char.get("last_updated", "")
                
                if json_time > mongo_time:
                    #JSON is newer, update DB
                    store.update_one({"_id": ObjectId(_id)}, {"$set": json_char}, upsert=True)
                    merged_data[_id] = json_char
                else:
                    #MongoDb is newer or same, update JSON
                    merged_data[_id] = mongo_char
                    
            elif json_char and not mongo_char:
                #only in JSON, insert into DB
                result = store.insert_one(json_char)
                json_char["_id"] = str(result.inserted_id)
                merged_data[str(result.inserted_id)] = json_char
                
            elif mongo_char and not json_char:
                #only in DB, add to JSON
                merged_data[_id] = mongo_char
                
        #Convert any ObjectIds back to strings for JSON saving
        for key, char in merged_data.items():
            if "_id" in char and isinstance(char["_id"], ObjectId):
                char["_id"] = str(char["_id"])
                
        #write merged data back to JSON file
        with open(file, "w") as f:
            json.dump(merged_data, f, indent=4)
            
            