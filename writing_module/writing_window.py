import uuid

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QComboBox,
    QColorDialog,
    QLabel,
    QLineEdit,
    QFileDialog,
)

from PySide6.QtGui import (
    QTextCharFormat,
    QFont,
    QTextListFormat,
    QTextCursor,
    QFontDatabase,
)

from PySide6.QtCore import Signal, Qt

from .indented_textEditor import IndentedTextEdit

# alternate layout manager


class WritingModule(QWidget):
    document_saved = Signal()

    def __init__(self, store):
        super().__init__()

        self.setWindowTitle("Writer")
        self.setMinimumSize(600, 750)

        self.store = store
        self.doc_id = str(uuid.uuid4())

        container = QWidget()
        container_layout = QVBoxLayout(container)

        # formatting buttons
        toolbar_layout = QHBoxLayout()

        # font selector
        self.font_selector = QComboBox()
        self.font_selector.addItems(QFontDatabase().families())
        self.font_selector.setCurrentText("Arial")
        self.font_selector.currentTextChanged.connect(self.set_editor_font)
        toolbar_layout.addWidget(self.font_selector)

        # font size dropdown
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(i) for i in range(8, 30, 2)])
        self.font_size_combo.setCurrentText("12")
        self.font_size_combo.currentTextChanged.connect(self.set_font_size)
        self.font_size_combo.setFixedWidth(65)
        toolbar_layout.addWidget(self.font_size_combo)

        # text color button
        self.color_btn = QPushButton("Color")
        self.color_btn.clicked.connect(self.set_text_color)
        self.color_btn.setFixedWidth(65)
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

        # images
        img_btn = QPushButton("⬅️📷")  # emoji icon
        img_btn.setToolTip("Insert Image Left Side")
        img_btn.clicked.connect(lambda: self.open_image_dialog("left"))
        toolbar_layout.addWidget(img_btn)

        r_img_btn = QPushButton("📷➡️")  # emoji icon
        r_img_btn.setToolTip("Insert Image Right Side")
        r_img_btn.clicked.connect(lambda: self.open_image_dialog("right"))
        toolbar_layout.addWidget(r_img_btn)

        container_layout.addLayout(toolbar_layout)

        # title field
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Title:"))
        self.title_input = QLineEdit()
        title_layout.addWidget(self.title_input)
        container_layout.addLayout(title_layout)

        # text editor and headings
        text_editor_container = QHBoxLayout()

        # font_modifications buttons container
        font_mod_container = QVBoxLayout()

        # headings buttons
        h1_btn = QPushButton("H1")
        h1_btn.clicked.connect(lambda: self.set_heading_level(1))
        h2_btn = QPushButton("H2")
        h2_btn.clicked.connect(lambda: self.set_heading_level(2))
        h3_btn = QPushButton("H3")
        h3_btn.clicked.connect(lambda: self.set_heading_level(3))
        h4_btn = QPushButton("H4")
        h4_btn.clicked.connect(lambda: self.set_heading_level(4))
        h5_btn = QPushButton("H5")
        h5_btn.clicked.connect(lambda: self.set_heading_level(5))
        h6_btn = QPushButton("H6")
        h6_btn.clicked.connect(lambda: self.set_heading_level(6))
        for b in [h1_btn, h2_btn, h3_btn, h4_btn, h5_btn, h6_btn]:
            b.setFixedWidth(65)
            font_mod_container.addWidget(b)

        # bullet list button
        bullet_btn = QPushButton("•B")
        bullet_btn.clicked.connect(self.insert_bullet_list)
        bullet_btn.setFixedWidth(65)
        font_mod_container.addWidget(bullet_btn)

        # bold
        bold_btn = QPushButton("B")
        bold_btn.setCheckable(True)
        bold_btn.clicked.connect(self.toggle_bold)
        bold_btn.setFixedWidth(65)
        font_mod_container.addWidget(bold_btn)

        # italic
        italic_btn = QPushButton("I")
        italic_btn.setCheckable(True)
        italic_btn.clicked.connect(self.toggle_italic)
        italic_btn.setFixedWidth(65)
        font_mod_container.addWidget(italic_btn)

        # underline
        underline_btn = QPushButton("U")
        underline_btn.setCheckable(True)
        underline_btn.clicked.connect(self.toggle_underline)
        underline_btn.setFixedWidth(65)
        font_mod_container.addWidget(underline_btn)

        text_editor_container.addLayout(font_mod_container)

        # text editor space
        self.textEditSpace = IndentedTextEdit(
            font_selector=self.font_selector, font_size_combo=self.font_size_combo
        )
        self.textEditSpace.setText("Write here...")
        self.textEditSpace.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Default
        text_editor_container.addWidget(self.textEditSpace)

        container_layout.addLayout(text_editor_container)

        # action buttons
        self.button_layout = QHBoxLayout()

        # save button
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_text)
        self.button_layout.addWidget(self.save_btn)
        # new document button
        self.new_doc_btn = QPushButton("New Doc")
        self.new_doc_btn.clicked.connect(self.create_new_doc)
        self.button_layout.addWidget(self.new_doc_btn)
        # clear text button
        self.clear_text_btn = QPushButton("Clear")
        self.clear_text_btn.clicked.connect(lambda: self.textEditSpace.clear())
        self.button_layout.addWidget(self.clear_text_btn)

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
        font = self.font_selector.currentText()
        font_size = float(self.font_size_combo.currentText())
        self.store.save_document(self.doc_id, html_content, title, font, font_size)
        self.document_saved.emit()  # notify that save occurred

    def load_font_and_size(self, font, font_size):
        if font:
            self.font_selector.setCurrentText(font)
        if font_size:
            self.font_size_combo.setCurrentText(str(int(font_size)))

        # update editor formatting explicitly
        fmt = QTextCharFormat()
        fmt.setFontFamily(font or self.font_selector.currentText())
        fmt.setFontPointSize(float(font_size or self.font_size_combo.currentText()))
        self.textEditSpace.mergeCurrentCharFormat(fmt)
        self.textEditSpace.setCurrentFont(QFont(fmt.fontFamily(), fmt.fontPointSize()))

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

    def set_font_size(self, size: float):
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

    def set_heading_level(self, level: int):
        if level not in [1, 2, 3, 4, 5, 6]:
            return

        cursor = self.textEditSpace.textCursor()

        # 1) set heading level on the block
        block_fmt = cursor.blockFormat()
        try:
            block_fmt.setHeadingLevel(level)
        except Exception:
            pass

        cursor.setBlockFormat(block_fmt)

        # 2 set font size & family as a character format
        char_fmt = QTextCharFormat()
        char_fmt.setFontFamily("Lexend")  # font setting here done on charFormat

        match level:
            case 1:
                char_fmt.setFontPointSize(24)
                char_fmt.setFontWeight(QFont.Weight.Bold)
            case 2:
                char_fmt.setFontPointSize(20)
                char_fmt.setFontWeight(QFont.Weight.Bold)
            case 3:
                char_fmt.setFontPointSize(18)
                char_fmt.setFontWeight(QFont.Weight.Bold)
            case 4:
                char_fmt.setFontPointSize(16)
            case 5:
                char_fmt.setFontPointSize(14)
            case 6:
                char_fmt.setFontPointSize(12)

        # apply to current block
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.mergeCharFormat(char_fmt)

        # # 3) Reset *future* text to normal after heading
        # normal_fmt = QTextCharFormat()
        # normal_fmt.setFontFamily(self.font_selector.currentText())
        # normal_fmt.setFontPointSize(float(self.font_size_combo.currentText()))
        # self.textEditSpace.mergeCurrentCharFormat(normal_fmt)

        # set current typing format to the heading *so typing in this block remains heading*
        self.textEditSpace.mergeCurrentCharFormat(char_fmt)

        # 4) Restore focus to editor
        self.textEditSpace.setFocus()

    def set_editor_font(self, font_name):
        font = QFont(font_name, int(self.font_size_combo.currentText()))
        # self.textEditSpace.setFont(font)
        cursor = self.textEditSpace.textCursor()
        fmt = QTextCharFormat()
        fmt.setFontFamily(
            font.family()
        )  # passing just the font family name from font object
        # maintain font size:
        fmt.setFontPointSize(float(self.font_size_combo.currentText()))

        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
        else:
            self.textEditSpace.mergeCurrentCharFormat(fmt)

    def merge_format_on_selection(self, format):
        cursor = self.textEditSpace.textCursor()
        if not cursor.hasSelection():
            cursor.select(cursor.SelectionType.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.textEditSpace.mergeCurrentCharFormat(format)

    # image handling

    def open_image_dialog(self, left_or_right):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.textEditSpace.insert_image(file_path, align=left_or_right)
