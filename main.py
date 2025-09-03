import sys
from app import app
from PySide6.QtWidgets import QApplication
from visual_app import CharacterApp


# qt_app = QApplication([])

# while True:
#     app(qt_app)
#     user_continue = input("Continue? (y/n)").lower()
#     if user_continue == "n":
#         break


def main():
    app = QApplication(sys.argv)
    window = CharacterApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
