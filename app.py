import pprint
from character_module import Character
from visual import ShowWidget
from character_module.db import character_store


def app(qt_app):
    # hold open widgets
    open_windows = []

    Character._ensure_character_file("characters.json")

    u_choice = input(
        "Select mode\nC for Create Character, L for Load Character with an option to modify, D for delete character, S to sync\n"
    )

    if u_choice.lower() == "c":
        c_name = input("Name your character\n")
        character = Character(name=c_name, store=character_store)
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
            Character.show_characters(store=character_store)
            u_sel_db = input("Select character from database or loc to use local:\n")
            loaded_character = Character.load_by_name(
                char_name=u_sel_db, store=character_store
            )
            print(loaded_character.name)

            # Show Visual Window
            widget = ShowWidget(data=loaded_character.__dict__)
            widget.destroyed.connect(lambda: open_windows.remove(widget))
            widget.show()
            open_windows.append(widget)
            qt_app.processEvents()  # allow UI to render

            # input("Press enter to close window...")
            # widget.close()

            u_db_up = input("Update character? (y/n)")
            if u_db_up == "y":
                widget.close()
                loaded_character.update_db()

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

    if u_choice.lower() == "s":
        sync_choice = input(
            "Sync mode: (push: json→db, pull: db→json, bi-directional: bidirectional):\n"
        ).lower()
        if sync_choice == "push":
            Character.sync_json_to_db(store=character_store)
        elif sync_choice == "pull":
            Character.sync_db_to_json(store=character_store)
        elif sync_choice == "bidirectional":
            Character.sync_bi_directional(store=character_store)
        else:
            print("Invalid sync option.")


if __name__ == "__main__":
    app()
