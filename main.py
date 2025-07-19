# import json

# class Character:
#     def __init__(self, name="", handle="", sex="", age="", role="", description="", experience_level="Novice", major_skills=[], minor_skills=[], cyberware=[], relationships=None):
#         self.name = name
#         self.handle = handle
#         self.sex = sex
#         self.age = age
#         self.role = role
#         self.description = description
#         self.experience_level = experience_level
#         self.major_skills = major_skills
#         self.minor_skills = minor_skills
#         self.cyberware = cyberware
#         self.relationships = relationships
    
#     def load_data(self, data):
        
#         self.name = data["Name"]
#         self.handle = data["Handle"]
#         self.sex = data["Sex"]
#         self.age = data["Age"]
#         self.role = data["Role"]
#         self.description = data["Description"]
#         self.experience_level = data["Experience Level"]
#         self.major_skills = data["Major Skills"]
#         self.minor_skills = data["Minor Skills"]
#         self.cyberware = data["Cyberware"]
#         self.relationships = data["Relationships"]

# def convert_json_data(file):
#     with open(file, 'r') as f:
#         data = json.load(f)
#         # print(f"This is the data: {data}")
#         key_list = [k for k in data.keys()]
#         print("These are the characters in the file:", key_list)
#     user_i = input("Select Character to Convert\n")
#     # print(f"The converting character {data[user_i]}")
#     return data[user_i]

# def make_character():
#     data_dict = convert_json_data("characters.json")
#     empty = Character()
#     empty.load_data(data_dict)
#     return empty

# casey_lane = make_character()
# print(casey_lane.name)

import json

class Character:
    def __init__(self, name="", handle="", sex="", age="", role="", description="",
                 experience_level="Novice", major_skills=None, minor_skills=None,
                 cyberware=None, relationships=None):
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


def convert_json_data(file):
    with open(file, 'r') as f:
        data = json.load(f)
        # key_list = list(data.keys())
        print("These are the characters in the file:", [data[item]['name'] for item in data])
    user_i = input("Select Character:\n")
    for d_item in data:
        if user_i == data[d_item]['name']:
            return data[d_item]
    return None
    # return data[user_i]

def make_character():
    data_dict = convert_json_data("characters.json")
    if data_dict != None:
        return Character.from_dict(data_dict)
    else:
        return data_dict

# casey_lane = make_character()
# print(casey_lane.name)

u_choice = input("Select mode\nC for Create Character, L for Load Character with an option to modify, D for delete character\n")

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
    c_relationships = input("Enter character's personal relationships, separated by a comma.\n")
    character.relationships = c_relationships.split(",")

    print(character.__dict__.items())

    c_save = input("Save?\n")
    if c_save.lower() == "yes":
        character.to_json("characters.json")
    else:
        print("End of Line.")

if u_choice.lower() == 'l':
    character = make_character()
    if character != None:
        print(character.__dict__.items())
        u_yn = input("Would you like to edit features?\n")
        if u_yn.lower() != "y" or u_yn.lower() != "n":
            print("invalid input")
        if u_yn.lower() == 'y':
            key_list = []
            for key, value in character.__dict__.items():
                print(key)
                key_list.append(key)
            u_select = input("Select a value to change from the list:\n")
            if u_select in key_list:
                char_dict = {key: value for key, value in character.__dict__.items()}
                chg_val = input(f"{u_select} - Change Value to:\n")
                char_dict[u_select] = chg_val
                new_character = Character.from_dict(char_dict)
                new_character.to_json("characters.json")
                print(new_character.__dict__.items())
        else:
            print("Load completed.")
        
if u_choice.lower() == "d":
    file = "characters.json"
    with open(file, "r") as f:
        data = json.load(f)
        print([name.replace("_", " ") for name in data.keys()])
        file_name = input("Select character to delete:\n")
        del data[file_name.replace(" ", "_")]
        
    with open(file, "w") as fi:
        json.dump(data, fi, indent=4)
