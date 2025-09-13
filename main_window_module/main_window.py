from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QListWidget,
    QMessageBox,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QScrollArea,
    QTabWidget,
    QDialog,
    QSplitter,
    QApplication,
    QComboBox,
    QColorDialog,
)

from PySide6.QtGui import QTextCharFormat, QFont, QColor

from PySide6.QtCore import Qt

from character_module import CharacterApp

from writing_module import WritingModule


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Character Record & Story App")
        self.setMinimumSize(1280, 815)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_window = CharacterApp()
        splitter.addWidget(left_window)

        # placeholder /right panes
        # splitter.addWidget(RightPane())
        central_window = WritingModule()
        splitter.addWidget(central_window)

        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

        # ---- center on screen ----
        self.center_on_screen()

    # methods
    def center_on_screen(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()

        # move to center
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
