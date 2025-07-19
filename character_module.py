import json
import pprint
from collections import OrderedDict


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

    @staticmethod
    def convert_json_data(file):
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
    def make_character(cls):
        data_dict = cls.convert_json_data("characters.json")
        if data_dict != None:
            return Character.from_dict(data_dict)
        else:
            return data_dict

    @staticmethod
    def delete_character():
        file = "characters.json"
        with open(file, "r") as f:
            data = json.load(f)
            print([name.replace("_", " ") for name in data.keys()])
            file_name = input("Select character to delete:\n")
            del data[file_name.replace(" ", "_")]

        with open(file, "w") as fi:
            json.dump(data, fi, indent=4)


def app():
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

        c_save = input("Save?\n")
        if c_save.lower() == "yes":
            character.to_json("characters.json")
        else:
            print("End of Line.")

    if u_choice.lower() == "l":
        character = Character.make_character()
        if character != None:
            pprint.pprint(character.as_ordered_dict())
            u_yn = input("Would you like to edit features?\n").lower()
            if u_yn.lower() not in ["y", "n"]:
                print("invalid input")
            if u_yn.lower() == "y":
                while True:
                    print("\nEditable fields:")
                    for key in character.__dict__:
                        print(f"- {key}")

                    u_select = input("Select a value to change from the list:\n")
                    if u_select.lower() == "done":
                        break
                    if u_select in character.__dict__:
                        chg_val = input(f"{u_select} - Change Value to:\n")
                        character.update_field(u_select, chg_val)
                    else:
                        print("Invalid field. Try again!")
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
