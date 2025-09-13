from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QMessageBox,
)

from PySide6.QtCore import Signal

from writing_module import WritingStore


class FileModule(QWidget):
    """Right-side panel that manages the list of documents."""

    delete_signal = Signal()

    def __init__(self, store, on_doc_selected=None, on_new_doc=None):
        """
        :param on_doc_selected: callback(doc_id) when user clicks a document
        :param on_new_doc: callback() when user clicks New Document
        """
        super().__init__()

        self.setMinimumWidth(150)

        self.store = store
        self.on_doc_selected = on_doc_selected
        self.on_new_doc = on_new_doc

        layout = QVBoxLayout(self)

        # __document list__
        self.doc_list = QListWidget()
        self.doc_list.itemClicked.connect(self.handle_doc_click)
        layout.addWidget(self.doc_list)

        # --buttons--
        button_layout = QHBoxLayout()

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_document)
        button_layout.addWidget(self.delete_btn)

        layout.addLayout(button_layout)

        self.refresh_list()

        # methods

    def refresh_list(self):
        """Reload the list from storage."""
        self.doc_list.clear()
        for doc_id, meta in self.store.index.items():
            title = meta.get("title", "(untitled)")
            item = QListWidgetItem(f"{title} ({doc_id[:8]})")
            item.setData(256, doc_id)
            self.doc_list.addItem(item)

    def handle_doc_click(self, item):
        if self.on_doc_selected:
            self.on_doc_selected(item.data(256))

    def new_document(self):
        if self.on_new_doc:
            self.on_new_doc()
        self.doc_list.clearSelection()

    def delete_document(self):
        """Deletes selected document with confirmation."""
        item = self.doc_list.currentItem()
        if not item:
            return

        doc_id = item.data(256)
        title = self.store.index.get(doc_id, {}).get("title", "Untitled")

        confirm = QMessageBox.question(
            self,
            "Delete Document",
            f"Are you sure you want to delete '{title}' ?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            self.store.delete_document(doc_id)
            self.refresh_list()
            self.delete_signal.emit()
