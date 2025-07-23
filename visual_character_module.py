from datetime import datetime, timezone
import uuid

class Character:
    def __init__(self, store, data=None):
        self.store = store
        self._id = str(uuid.uuid4())
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
            self.load_from_dict(data)

    def load_from_dict(self, data):
        for k, v in data.items():
            setattr(self, k, v)

    def to_dict(self):
        return {
            "_id": self._id,
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