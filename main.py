from character_module import *

while True:
    app()
    user_continue = input("Continue? (y/n)").lower()
    if user_continue == "n":
        break
