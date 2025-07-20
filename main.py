from app import app

while True:
    app()
    user_continue = input("Continue? (y/n)").lower()
    if user_continue == "n":
        break
