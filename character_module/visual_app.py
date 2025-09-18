import os
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
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

# from character_store import CharacterStore
from .visual_character_module import Character

# from db import character_store as store
from .db import get_data_stores

# from items tab import the items and tab
from .items_tab import ItemsTab

# clickable label:
from .ClickableLabel import ClickableLabel


class CharacterApp(QWidget):
    def __init__(self, pdf_generator, logger):
        super().__init__()
        self.setWindowTitle("Character Manager")
        self.setMinimumSize(400, 800)  # avoid fixed height

        self.logger = logger

        # database stores
        stores = get_data_stores()
        self.logger.debug("stores loaded.")
        self.store = stores.get("character_store")
        self.items_collection = stores.get("newItems", None)
        self.cyberware_items = stores.get("cyberware_items", None)
        self.current_char = None
        self.editing = False

        # pdf gen
        self.pdf_generator = pdf_generator
        self.logger.debug("PDF Generator loaded")

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Container inside scroll
        scroll_content = QWidget()
        scroll.setWidget(scroll_content)

        # Layout for scroll content
        main_layout = QVBoxLayout(scroll_content)

        # Create UI inside scroll_content
        self.init_ui(main_layout)

        # Main layout adds the scroll area
        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # create character tab
        character_tab = QWidget()
        character_layout = QVBoxLayout(character_tab)

        character_layout.addWidget(scroll)
        self.tabs.addTab(character_tab, "Characters")

        for cname, collection in stores.items():
            if cname == "character_store":
                continue
            if cname == "characters":
                continue

            if not hasattr(collection, "find_one"):
                continue  # probably JSON fallback or unavailable

            try:
                sample_doc = collection.find_one()
            except Exception:
                continue

            if not sample_doc:
                continue

            columns = list(sample_doc.keys())
            columns = [c for c in columns if "name" in c or "cost" in c or "item" in c]

            tab = ItemsTab(collection, columns=columns)
            self.tabs.addTab(tab, cname.capitalize())

        self.load_all_characters()
        self.logger.debug("All Characters loaded.")

    def init_ui(self, parent_layout):
        self.logger.debug("initializing character layout")
        # character list
        self.list_widget = QListWidget()
        self.list_widget.setMaximumHeight(75)
        self.list_widget.itemClicked.connect(self.load_selected_character)
        parent_layout.addWidget(self.list_widget)

        # top row image & short fields:
        top_row = QHBoxLayout()

        # image
        self.image_label = ClickableLabel("[No Image]")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(250, 200)
        self.image_label.clicked.connect(self.open_full_image)

        left_col = QVBoxLayout()
        left_col.addWidget(self.image_label)

        # path row
        image_path_layout = QHBoxLayout()
        self.image_path_input = QLineEdit()
        self.image_path_input.setReadOnly(True)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_image)
        self.browse_btn.setEnabled(False)
        image_path_layout.addWidget(QLabel("Path: "))
        image_path_layout.addWidget(self.image_path_input)
        image_path_layout.addWidget(self.browse_btn)

        left_col.addLayout(image_path_layout)
        top_row.addLayout(left_col)

        # right-side short fields:
        quick_form = QFormLayout()
        self.inputs = {}
        self.inputs["image_path"] = self.image_path_input

        short_fields = ["name", "handle", "sex", "age", "role", "experience_level"]
        for field in short_fields:
            widget = QLineEdit()
            widget.setReadOnly(True)
            self.inputs[field] = widget
            quick_form.addRow(field.capitalize(), widget)

        top_row.addLayout(quick_form)
        parent_layout.addLayout(top_row)

        # --- long text fields (full width)---
        long_form = QFormLayout()
        multiline_fields = [
            "description",
            "major_skills",
            "minor_skills",
            "cyberware",
            "relationships",
            # "background",
        ]

        for field in multiline_fields:
            widget = QTextEdit()
            widget.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
            widget.setReadOnly(True)
            widget.setMaximumHeight(200)
            self.inputs[field] = widget
            long_form.addRow(field.capitalize(), widget)

        # background field
        background_widget = QTextEdit()
        background_widget.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        background_widget.setReadOnly(True)
        background_widget.setMinimumHeight(250)
        self.inputs["background"] = background_widget
        long_form.addRow("Background", background_widget)

        parent_layout.addLayout(long_form)

        # buttons at bottom
        btn_layout = QHBoxLayout()

        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self.new_character)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self.edit_character)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_character)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_character)

        self.print_btn = QPushButton("PDF")
        self.print_btn.clicked.connect(self.print_to_pdf)

        for b in (
            self.new_btn,
            self.edit_btn,
            self.save_btn,
            self.delete_btn,
            self.print_btn,
        ):
            btn_layout.addWidget(b)

        # layout.addLayout(btn_layout)
        parent_layout.addLayout(btn_layout)

    # methods

    def load_all_characters(self):
        self.logger.info("Bi-directional Sync initiated.")
        Character.sync_bi_directional(store=self.store)
        self.list_widget.clear()
        character_list = list(self.store.find())
        self.sorted_characters = sorted(character_list, key=lambda x: x["name"])
        for char in self.sorted_characters:
            self.list_widget.addItem(f"{char.get('name')} ({char.get('handle')})")
        self.logger.info("Sync completed.")

    def get_selected_character_data(self):
        index = self.list_widget.currentRow()
        return (
            self.sorted_characters[index]
            if 0 <= index < len(self.sorted_characters)
            else None
        )

    def load_selected_character(self):
        data = self.get_selected_character_data()
        self.logger.debug("Getting data for character")

        if not data:
            self.logger.debug("Failed to get data.")
            return

        self.current_char = Character(self.store, data=data)
        self.logger.debug(f"Got character")

        for field in self.inputs:
            val = getattr(self.current_char, field)
            display_text = ", ".join(val) if isinstance(val, list) else str(val)
            if isinstance(self.inputs[field], QTextEdit):
                self.inputs[field].setPlainText(display_text)
            else:
                self.inputs[field].setText(display_text)

            self.inputs[field].setReadOnly(True)

        image_path = getattr(self.current_char, "image_path", "").strip('"')
        if image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path).scaledToHeight(
                200, Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(pixmap)
            self.load_image(image_path)
            self.image_path_input.setText(image_path)
        else:
            self.image_label.setText("[No Image]")

        self.editing = False

    def new_character(self):
        self.image_path_input.setText("")
        self.image_label.setText("[No Image]")
        self.current_char = Character(self.store)
        for field in self.inputs:
            self.inputs[field].clear()
            self.inputs[field].setReadOnly(False)

        self.image_path_input.setReadOnly(False)
        self.image_path_input.clear()

        self.editing = True
        self.save_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)

    def edit_character(self):
        if not self.current_char:
            QMessageBox.warning(self, "Error", "No character loaded")
            return
        for field in self.inputs:
            self.inputs[field].setReadOnly(False)
        self.image_path_input.setReadOnly(False)
        self.editing = True
        self.save_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)

    def save_character(self):
        if not self.current_char:
            self.current_char = Character(self.store)

        for field, input_box in self.inputs.items():
            val = (
                input_box.toPlainText()
                if isinstance(input_box, QTextEdit)
                else input_box.text()
            )
            if field in ["major_skills", "minor_skills", "cyberware", "relationships"]:
                val = [s.strip() for s in val.split(",") if s.strip()]
            setattr(self.current_char, field, val)

        image_path = self.image_path_input.text()
        self.current_char.image_path = image_path

        self.current_char.save_to_store()
        self.load_all_characters()
        QMessageBox.information(self, "Saved", "Chracter saved successfully.")
        # Reset fields to read-only
        for input_box in self.inputs.values():
            input_box.setReadOnly(True)

        self.image_path_input.setReadOnly(True)

        self.editing = False
        self.save_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)

    def delete_character(self):
        if not self.current_char:
            QMessageBox.warning(self, "Error", "No character Selected")
            return
        confirm = QMessageBox.question(self, "Delete", "Delte this character?")
        if confirm == QMessageBox.StandardButton.Yes:
            self.current_char.delete_from_store()
            self.load_all_characters()
            self.current_char = None
            for field in self.inputs:
                self.inputs[field].clear()
            QMessageBox.information(self, "Deleted", "Character Deleted.")

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.image_path_input.setText(file_path)
            self.load_image(file_path)

    def load_image(self, path):
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            scaled = pixmap.scaledToHeight(
                200, Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText("[No Image]")

    def open_full_image(self):
        if not self.current_char or not getattr(self.current_char, "image_path", None):
            return

        image_path = self.current_char.image_path
        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            return

        # create popup window

        dlg = QDialog(self)
        dlg.setWindowTitle(self.current_char.name)
        dlg.setMinimumSize(self.width(), self.height())  # same size as window UI

        # position relative to parent:
        parent_pos = self.pos()
        dlg.move(parent_pos.x() + 50, parent_pos.y() + 50)

        layout = QVBoxLayout(dlg)

        img_label = QLabel()
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # scale pixmap to dialog size
        scaled = pixmap.scaled(
            dlg.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        img_label.setPixmap(scaled)

        layout.addWidget(img_label)

        # rescale when resizing
        def resize_event(event):
            new_scaled = pixmap.scaled(
                dlg.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            img_label.setPixmap(new_scaled)
            return QDialog.resizeEvent(dlg, event)

        dlg.resizeEvent = resize_event
        dlg.exec()

    def print_to_pdf(self):
        self.pdf_generator.generate_character_sheet(self.current_char.to_dict())
