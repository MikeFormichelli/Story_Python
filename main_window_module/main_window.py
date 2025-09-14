from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QApplication,
)

from PySide6.QtGui import QTextCharFormat, QFont, QColor

from PySide6.QtCore import Qt, QTimer

from character_module import CharacterApp

from writing_module import WritingModule, WritingStore

from file_module import FileModule


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Character Record & Story App")
        self.setMinimumSize(1530, 815)

        self.store = WritingStore()

        splitter = QSplitter(Qt.Orientation.Horizontal)

        character_pane = CharacterApp()
        splitter.addWidget(character_pane)

        self.writing_pane = WritingModule(store=self.store)
        splitter.addWidget(self.writing_pane)

        file_pane = FileModule(
            store=self.store,
            on_doc_selected=self.load_document,
            on_new_doc=self.create_new_document,
        )
        splitter.addWidget(file_pane)

        # ✅ Connect the signal from WritingModule to refresh file list
        self.writing_pane.document_saved.connect(file_pane.refresh_list)
        file_pane.delete_signal.connect(self.writing_pane.create_new_doc)

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

    def load_document(self, doc_id):
        """Called when FileModule selects a document"""
        store = WritingStore()
        html = store.get_document(doc_id)
        meta = store.index.get(doc_id, {})
        self.writing_pane.doc_id = doc_id
        self.writing_pane.textEditSpace.setHtml(html or "")
        self.writing_pane.title_input.setText(meta.get("title", ""))
        self.writing_pane.load_font_and_size(
            meta.get("font", "Garamond"), meta.get("font_size", "12")
        )

    def create_new_document(self):
        """Called when FileModule creates a new doc."""
        self.writing_pane.create_new_document()
