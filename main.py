import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from main_window_module import MainWindow


def main():
    app = QApplication(sys.argv)

    # set default app font
    app_font = QFont("Garamond", 12)
    app.setFont(app_font)

    # --show main window --

    window = MainWindow()
    window.setStyleSheet("background-color: #191D21")
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
