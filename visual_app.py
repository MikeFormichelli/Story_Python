import sys
import os
from PySide6.QtWidgets import (
    QApplication,
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
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

# from character_store import CharacterStore
from visual_character_module import Character
from db import character_store as store


class CharacterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Character Manager")
        self.setMinimumSize(400, 600)  # avoid fixed height
        # self.store = CharacterStore(db=connect_to_db())
        self.store = store
        self.current_char = None
        self.editing = False

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        # Container inside scroll
        scroll_content = QWidget()
        scroll.setWidget(scroll_content)

        # Layout for scroll content
        self.form_layout = QVBoxLayout(scroll_content)

        # Create UI inside scroll_content
        self.init_ui()

        # Main layout adds the scroll area
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

        self.load_all_characters()

    def init_ui(self):
        # layout = QVBoxLayout(parent_widget)
        layout = self.form_layout

        # image path input + browse

        # character list
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.load_selected_character)
        layout.addWidget(self.list_widget)

        # image
        image_path_layout = QHBoxLayout()
        self.image_path_input = QLineEdit()
        self.image_path_input.setReadOnly(True)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.browse_image)
        self.browse_btn.setEnabled(False)
        image_path_layout.addWidget(QLabel("Image Path: "))
        image_path_layout.addWidget(self.image_path_input)
        image_path_layout.addWidget(self.browse_btn)
        self.image_label = QLabel("[No Image]")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedHeight(200)
        layout.addWidget(self.image_label)
        layout.addLayout(image_path_layout)

        # form
        self.form = QFormLayout()
        self.inputs = {}
        self.inputs["image_path"] = self.image_path_input
        for field in [
            "name",
            "handle",
            "sex",
            "age",
            "role",
            "description",
            "experience_level",
            "major_skills",
            "minor_skills",
            "cyberware",
            "relationships",
        ]:
            # Fields that should use QTextEdit
            multiline_fields = {
                "description",
                "relationships",
                "major_skills",
                "minor_skills",
                "cyberware",
            }

            if field in multiline_fields:
                widget = QTextEdit()
                widget.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
                widget.setReadOnly(True)
                widget.setFixedHeight(60)  # adjust as needed
            else:
                widget = QLineEdit()
                widget.setReadOnly(True)

            self.inputs[field] = widget
            self.form.addRow(field.capitalize(), widget)

        layout.addLayout(self.form)

        # buttons
        btn_layout = QHBoxLayout()

        self.new_btn = QPushButton("New")
        self.new_btn.clicked.connect(self.new_character)
        btn_layout.addWidget(self.new_btn)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self.edit_character)
        btn_layout.addWidget(self.edit_btn)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_character)
        btn_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_character)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)
        # self.setLayout(layout)

    # methods
    def load_all_characters(self):
        Character.sync_bi_directional(store=store)
        self.list_widget.clear()
        for char in self.store.find():
            self.list_widget.addItem(f"{char.get('name')} ({char.get('handle')})")

    def get_selected_character_data(self):
        index = self.list_widget.currentRow()
        all_chars = list(self.store.find())
        return all_chars[index] if 0 <= index < len(all_chars) else None

    def load_selected_character(self):
        data = self.get_selected_character_data()
        if not data:
            return
        self.current_char = Character(self.store, data=data)
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


def main():
    app = QApplication(sys.argv)
    window = CharacterApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
