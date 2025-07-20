from app import app
from PySide6.QtWidgets import QApplication

qt_app = QApplication([])

while True:
    app(qt_app)
    user_continue = input("Continue? (y/n)").lower()
    if user_continue == "n":
        break
