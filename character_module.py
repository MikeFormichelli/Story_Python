import json
import os
import uuid
from collections import OrderedDict
from datetime import datetime, timezone
from bson import ObjectId
import textwrap
from db import characters_collection

class Character:
    def __init__(
        self,
        name="",
        handle="",
        sex="",
        age="",
        role="",
        description="",
        experience_level="Novice",
        major_skills=None,
        minor_skills=None,
        cyberware=None,
        relationships=None,
        _id=None,
        last_updated=None,
        **kwargs
    ):
        self.name = name
        self.handle = handle
        self.sex = sex
        self.age = age
        self.role = role
        self.description = description
        self.experience_level = experience_level
        self.major_skills = major_skills or []
        self.minor_skills = minor_skills or []
        self.cyberware = cyberware or []
        self.relationships = relationships or []
        self._id = _id or str(uuid.uuid4()) #generate unique ids
        self.last_updated = last_updated or datetime.now(timezone.utc).isoformat()
        
        #absorb kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    #db functions
    def to_dict(self):
        return self.__dict__
    
    def save_to_db(self):
        self._stamp()
        
        existing = characters_collection.find_one({"_id": self._id})
        if existing:
            print("Character already exists in database")
            return
        characters_collection.insert_one(self.to_dict())
        
    def update_db(self):
        while True:
            fresh_data = characters_collection.find_one({"_id": self._id})
            if not fresh_data:
                print("Character not found in database.")
                return
            self.__dict__.update(fresh_data)
            
            print("\nEditable fields:")
            # for key in self.__dict__:
            #     if key in ["name", "_id"]:
            #         continue  # skip name
            #     print(f"- {key} (current: {self.__dict__[key]})")
            self.get_editable_fields()

            u_select = input(
                "Select a value to change from the list (done if finished):\n"
            )
            if u_select.lower() == "done":
                break
            
            if u_select in self.__dict__ and u_select not in ["name", "_id"]:
                current_value = self.__dict__[u_select]
                print(f"Current value for {u_select}: {current_value}")
                chg_val = input(f"{u_select} - Change Value to:\n")
                
                if isinstance(current_value, list):
                    new_val = [v.strip() for v in chg_val.split(",") if v.strip()]
                else:
                    new_val = chg_val
                    
                self._stamp()
                characters_collection.update_one({"_id": self._id}, {"$set": {u_select: new_val, "last_updated": self.last_updated}})
                print(f"Updated '{u_select}' successfully.")
            else:
                print("Invalid field. Try again!")
        # Final sync after all updates
        fresh_data = characters_collection.find_one({"_id": self._id})
        if fresh_data:
            self.__dict__.update(fresh_data)
            print("✅ Final sync complete. Character is up-to-date.")

    @classmethod
    def load_from_db(cls, char_id):
        data = characters_collection.find_one({"_id": char_id})
        if data:
            return cls(**data)
        return None
    
    @classmethod
    def show_characters(cls):
        print("Showing characters:")
        for char in characters_collection.find():
            print(f"- {char.get('name', '[Unnamed]')}")
        return 
    
    @classmethod
    def load_by_name(cls, char_name):
        data = characters_collection.find_one({"name": char_name})
        if data:
            return cls(**data)
        return None
    
    #class methods
    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            handle=data.get("handle", ""),
            sex=data.get("sex", ""),
            age=data.get("age", ""),
            role=data.get("role", ""),
            description=data.get("description", ""),
            experience_level=data.get("experience Level", "Novice"),
            major_skills=data.get("major_skills", []),
            minor_skills=data.get("minor_skills", []),
            cyberware=data.get("cyberware", []),
            relationships=data.get("relationships", []),
        )
    
    @classmethod
    def make_character(cls, file="characters.json"):
        data_dict = cls.select_character_from_file(file)
        if data_dict != None:
            return Character.from_dict(data_dict)
        else:
            return data_dict
        
    #instance methods
    def _stamp(self):
        self.last_updated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
    def get_editable_fields(self):
        for k in self.__dict__:
            if k not in ["name", "_id"]:
                print(f"FIELD: {k} - CURRENT: {self.__dict__[k]}")
        return

    def to_json(self, file):
        Character._ensure_character_file("characters.json")
        data_dict = {}
        for key, value in self.__dict__.items():
            data_dict[key] = value

        with open(file, "r") as f:
            data = json.load(f)
            file_name = self.name.replace(" ", "_")
            data[file_name] = data_dict

        with open(file, "w") as fi:
            json.dump(data, fi, indent=4)

    def update_field(self, field, value):
        if hasattr(self, field):
            attr = getattr(self, field)
            if isinstance(attr, list):
                setattr(self, field, [v.strip() for v in value.split(",")])
            else:
                setattr(self, field, value)

    def as_ordered_dict(self):
        data = OrderedDict()
        data["name"] = self.name
        for key, value in self.__dict__.items():
            if key != "name":
                data[key] = value
        return data

    def edit_fields_interactively(self):
        while True:
            print("\nEditable fields:")
            self.get_editable_fields()

            u_select = input(
                "Select a value to change from the list (done if finished):\n"
            )
            if u_select.lower() == "done":
                break
            if u_select in self.__dict__:
                current_value = self.__dict__[u_select]
                print(f"Current value for {u_select}: {current_value}")
                chg_val = input(f"{u_select} - Change Value to:\n")
                self.update_field(u_select, chg_val)
            else:
                print("Invalid field. Try again!")
    
    #static methods
    @staticmethod
    def select_character_from_file(file):
        Character._ensure_character_file("characters.json")
        with open(file, "r") as f:
            data = json.load(f)
            print(
                "These are the characters in the file:",
                [data[item]["name"] for item in data],
            )
        user_i = input("Select Character:\n")
        for d_item in data:
            if user_i == data[d_item]["name"]:
                return data[d_item]
        return None

    @staticmethod
    def delete_character():
        Character._ensure_character_file("characters.json")
        file = "characters.json"
        with open(file, "r") as f:
            data = json.load(f)
            print([name.replace("_", " ") for name in data.keys()])
            file_name = input("Select character to delete:\n")
            del data[file_name.replace(" ", "_")]

        with open(file, "w") as fi:
            json.dump(data, fi, indent=4)
        
        doomed_char = characters_collection.find_one({"name": file_name})
        characters_collection.delete_one({"_id": doomed_char.get("_id")})
        print(f"Character {file_name} successfully deleted! 💥")
        
    @staticmethod
    def _ensure_character_file(file="chracters.json"):
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump({}, f, indent=4)
            return
        try:
            with open(file, "r") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("Root JSON is not a dictionary.")
        except (json.JSONDecodeError, ValueError):
            print(f"[WARNING] {file} is corrupted or invalid. Resetting to empty.")
            with open(file, "w") as f:
                json.dump({}, f, indent=4)

    @staticmethod
    def sync_json_to_db(file="characters.json"):
        Character._ensure_character_file(file)
        with open(file, "r") as f:
            data = json.load(f)
        
        for name_key, char_data in data.items():
            raw_id = char_data.get("_id")
            
            try:
                char_data["_id"] = ObjectId(raw_id)
            except Exception:
                pass #leave as-is if it's not an ObjectId-like string
            
            existing = characters_collection.find_one({"_id": char_data.get("_id")})
            
            if existing:
                #update existing character
                characters_collection.update_one(
                    {"_id": char_data["_id"]}, {"$set": char_data}, upsert=True
                )
                print(f"🔄 Updated '{char_data['name']}' in database.")
            else:
                # Insert new character
                characters_collection.insert_one(char_data)
                print(f"⬆️  Inserted '{char_data['name']}' into database.")
    
    @staticmethod
    def sync_db_to_json(file="characters.json"):
        Character._ensure_character_file(file)

        data = {}
        for char in characters_collection.find():
            file_key = char["name"].replace(" ", "_")
            
            char["_id"] = str(char["_id"])
            
            data[file_key] = char

        with open(file, "w") as f:
            json.dump(data, f, indent=4)

        print(f"📥 Pulled {len(data)} characters from database to '{file}'.")
    
    @staticmethod
    def sync_bi_directional(file="chracters.json"):
        #load JSON
        with open(file, "r") as f:
            json_data = json.load(f)
            
        #load MongoDB Data
        mongo_data = {char["_id"]: char for char in characters_collection.find()}
        
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
                    characters_collection.update_one({"_id": _id}, {"$set": json_char}, upsert=True)
                    merged_data[_id] = json_char
                else:
                    #MongoDb is newer or same, update JSON
                    merged_data[_id] = mongo_char
                    
            elif json_char and not mongo_char:
                #only in JSON, insert into DB
                characters_collection.insert_one(json_char)
                merged_data[_id] = json_char
                
            elif mongo_char and not json_char:
                #only in DB, add to JSON
                merged_data[_id] = mongo_char
                
        #write merged data back to JSON file
        with open(file, "w") as f:
            json.dump(merged_data, f, indent=4)
