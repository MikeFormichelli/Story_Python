import uuid

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QHBoxLayout,
    QComboBox,
    QColorDialog,
    QLabel,
    QLineEdit,
)

from PySide6.QtGui import QTextCharFormat, QFont, QTextListFormat, QTextCursor

from PySide6.QtCore import Signal, Qt

from .writing_store import WritingStore


class IndentedTextEdit(QTextEdit):
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()

            # Get current line text
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            line_text = cursor.selectedText()

            # Count leading spaces/tabs for previous line
            leading_whitespace = ""
            for ch in line_text:
                if ch in (" ", "\t"):
                    leading_whitespace += ch
                else:
                    break

            # If line has no leading whitespace, use default indent
            indent = leading_whitespace or "    "

            # Let QTextEdit handle the newline first
            super().keyPressEvent(event)

            # Insert the indent
            self.insertPlainText(indent)
        else:
            super().keyPressEvent(event)


class WritingModule(QWidget):
    document_saved = Signal()

    def __init__(self, store):
        super().__init__()

        self.setWindowTitle("Writer")
        self.setMinimumSize(600, 800)

        self.store = store
        self.doc_id = str(uuid.uuid4())

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

        # Alignment buttons

        left_btn = QPushButton("Left")
        left_btn.clicked.connect(
            lambda: self.textEditSpace.setAlignment(Qt.AlignmentFlag.AlignLeft)
        )
        toolbar_layout.addWidget(left_btn)

        center_btn = QPushButton("Center")
        center_btn.clicked.connect(
            lambda: self.textEditSpace.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        )
        toolbar_layout.addWidget(center_btn)

        justify_btn = QPushButton("Justify")
        justify_btn.clicked.connect(
            lambda: self.textEditSpace.setAlignment(Qt.AlignmentFlag.AlignJustify)
        )
        toolbar_layout.addWidget(justify_btn)

        # bullet list button
        bullet_btn = QPushButton("• Bullet")
        bullet_btn.clicked.connect(self.insert_bullet_list)
        toolbar_layout.addWidget(bullet_btn)

        container_layout.addLayout(toolbar_layout)

        # title field
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Title:"))
        self.title_input = QLineEdit()
        title_layout.addWidget(self.title_input)
        container_layout.addLayout(title_layout)

        # text editor space
        self.textEditSpace = IndentedTextEdit()
        self.textEditSpace.setText("Write here...")
        self.textEditSpace.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Default
        container_layout.addWidget(self.textEditSpace)

        # action buttons
        self.button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_text)
        self.button_layout.addWidget(self.save_btn)
        self.new_doc_btn = QPushButton("New Doc")
        self.new_doc_btn.clicked.connect(self.create_new_doc)
        self.button_layout.addWidget(self.new_doc_btn)
        container_layout.addLayout(self.button_layout)

        # main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(container)

    # document handling methods

    def create_new_doc(self):
        """create a new empty document with a fresh UUID"""
        self.doc_id = str(uuid.uuid4())
        self.title_input.clear()
        self.textEditSpace.clear()

    def save_text(self):
        if not self.doc_id:
            self.create_new_doc()

        html_content = self.textEditSpace.toHtml()
        title = self.title_input.text().strip()
        self.store.save_document(self.doc_id, html_content, title)
        self.document_saved.emit()  # notify that save occurred

    def load_text(self):
        saved_html = self.store.get_document(self.doc_id)
        if saved_html:
            self.textEditSpace.setHtml(saved_html)

        saved_meta = self.store.index.get(self.doc_id, {})
        if "title" in saved_meta:
            self.title_input.setText(saved_meta["title"])

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

    def insert_bullet_list(self):
        cursor = self.textEditSpace.textCursor()
        cursor.insertList(QTextListFormat.Style.ListDisc)

    def merge_format_on_selection(self, format):
        cursor = self.textEditSpace.textCursor()
        if not cursor.hasSelection():
            cursor.select(cursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.textEditSpace.mergeCurrentCharFormat(format)
