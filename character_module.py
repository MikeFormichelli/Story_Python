import json
import pprint
import os
import uuid
from collections import OrderedDict
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
        _id=None
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
        
    #db functions
    def to_dict(self):
        return self.__dict__
    
    def save_to_db(self):
        characters_collection.insert_one(self.to_dict())
        
    @classmethod
    def load_from_db(cls, char_id):
        data = characters_collection.find_one({"_id": char_id})
        if data:
            return cls(**data)
        return None
    
    @classmethod
    def show_characters(cls):
        print(f"Showing characters:\n{[char["name"] for char in characters_collection.find()]}")
        return 
    
    @classmethod
    def load_by_name(cls, char_name):
        data = characters_collection.find_one({"name": char_name})
        if data:
            return cls(**data)
        return None
    
    #other functions
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
            for key in self.__dict__:
                if key == "name":
                    continue  # skip name

                print(f"- {key} (current: {self.__dict__[key]})")

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

    @classmethod
    def make_character(cls, file="characters.json"):
        data_dict = cls.select_character_from_file(file)
        if data_dict != None:
            return Character.from_dict(data_dict)
        else:
            return data_dict

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


def app():

    Character._ensure_character_file("characters.json")

    u_choice = input(
        "Select mode\nC for Create Character, L for Load Character with an option to modify, D for delete character\n"
    )

    if u_choice.lower() == "c":
        c_name = input("Name your character\n")
        character = Character(name=c_name)
        c_handle = input("Input character handle, if any. Select enter if none.\n")
        character.handle = c_handle
        c_sex = input("Enter character sex.\n")
        character.sex = c_sex
        c_age = input("Enter character age\n")
        character.age = c_age
        c_role = input("Enter character role\n")
        character.role = c_role
        c_desc = input("Enter character physical description.\n")
        character.description = c_desc
        c_major = input("Enter Character Major Skills separated by a comma.\n")
        character.major_skills = c_major.split(",")
        c_minor = input("Enter Character Minor Skills separated by a comma.\n")
        character.minor_skills = c_minor.split(",")
        c_cyber = input("Enter character cyberware, separated by a comma\n")
        character.cyberware = c_cyber.split(",")
        c_relationships = input(
            "Enter character's personal relationships, separated by a comma.\n"
        )
        character.relationships = c_relationships.split(",")

        print(character.__dict__.items())

        c_save = input("Save? (yes/no/db)\n")
        if c_save.lower() == "yes":
            character.to_json("characters.json")
        elif c_save.lower() == "db":
            character.save_to_db()
        else:
            print("End of Line.")

    if u_choice.lower() == "l":
        try:
            Character.show_characters()
            u_sel_db = input("Select character from database or loc to use local:\n")
            loaded_character = Character.load_by_name(u_sel_db)
            print(loaded_character.name)
            
        except Exception as e:
            print(e)
            
            character = Character.make_character()
            if character != None:
                pprint.pprint(character.as_ordered_dict())
                u_yn = input("Would you like to edit features? (y/n)\n").lower()
                if u_yn.lower() not in ["y", "n"]:
                    print("invalid input")

                if u_yn.lower() == "y":
                    character.edit_fields_interactively()

                    save = input("Save changes? (y/n)\n").lower()
                    if save == "y":
                        character.to_json("characters.json")
                        print("Character updated and saved.")
                    else:
                        print("Changes discarded.")
                else:
                    print("Load completed.")

    if u_choice.lower() == "d":
        Character.delete_character()


if __name__ == "__main__":
    app()
