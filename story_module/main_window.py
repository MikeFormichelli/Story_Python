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


class WritingModule(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Writer")
        self.setMinimumSize(600, 800)

        container = QWidget()
        container_layout = QVBoxLayout(container)

        # formatting buttons
        toolbar_layout = QHBoxLayout()

        # bold
        bold_btn = QPushButton("B")
        bold_btn.setCheckable(True)
        bold_btn.clicked.connect(self.toggle_bold)
        toolbar_layout.addWidget(bold_btn)

        # italic
        italic_btn = QPushButton("I")
        italic_btn.setCheckable(True)
        italic_btn.clicked.connect(self.toggle_italic)
        toolbar_layout.addWidget(italic_btn)

        # underline
        underline_btn = QPushButton("U")
        underline_btn.setCheckable(True)
        underline_btn.clicked.connect(self.toggle_underline)
        toolbar_layout.addWidget(underline_btn)

        # font size dropdown
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(i) for i in range(8, 30, 2)])
        self.font_size_combo.setCurrentText("12")
        self.font_size_combo.currentTextChanged.connect(self.set_font_size)
        toolbar_layout.addWidget(self.font_size_combo)

        # text color button
        self.color_btn = QPushButton("Color")
        self.color_btn.clicked.connect(self.set_text_color)
        toolbar_layout.addWidget(self.color_btn)

        container_layout.addLayout(toolbar_layout)

        # text editor space
        self.textEditSpace = QTextEdit()
        self.textEditSpace.setText("Write here...")
        container_layout.addWidget(self.textEditSpace)

        # save/action buttons
        self.button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_text)
        self.button_layout.addWidget(self.save_btn)
        container_layout.addLayout(self.button_layout)

        # main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)

    # database methods

    def save_text(self):
        pass

    # formatting methods

    def toggle_bold(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Weight.Bold if checked else QFont.Weight.Normal)
        self.merge_format_on_selection(fmt)

    def toggle_italic(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontItalic(checked)
        self.merge_format_on_selection(fmt)

    def toggle_underline(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(checked)
        self.merge_format_on_selection(fmt)

    def set_font_size(self, size):
        fmt = QTextCharFormat()
        fmt.setFontPointSize(float(size))
        self.merge_format_on_selection(fmt)

    def set_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self.merge_format_on_selection(fmt)

    def merge_format_on_selection(self, format):
        cursor = self.textEditSpace.textCursor()
        if not cursor.hasSelection():
            cursor.select(cursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.textEditSpace.mergeCurrentCharFormat(format)


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
