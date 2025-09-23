import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from main_window_module import MainWindow
from logging_module import logging_setup

# set directories
if not os.path.exists("logs"):
    os.makedirs("logs")

if not os.path.exists("data"):
    os.makedirs("data")

# set logger
logger = logging_setup()


def main():
    logger.info("\n\nStarting app")

    app = QApplication(sys.argv)

    # set default app font
    app_font = QFont("Garamond", 12)
    app.setFont(app_font)

    # --show main window --

    window = MainWindow(logger=logger)
    window.setStyleSheet("background-color: #191D21")
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
