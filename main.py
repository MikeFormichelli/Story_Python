import sys
from PySide6.QtWidgets import QApplication
from character_module import CharacterApp


def main():
    app = QApplication(sys.argv)
    window = CharacterApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
