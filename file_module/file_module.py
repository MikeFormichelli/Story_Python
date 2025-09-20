from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QMessageBox,
    QApplication,
)

from PySide6.QtCore import Signal, Qt


class FileModule(QWidget):
    """Right-side panel that manages the list of documents."""

    delete_signal = Signal()
    merge_signal = Signal(list)  # list of selected doc_ids

    def __init__(self, store, logger, on_doc_selected=None, on_new_doc=None):
        """
        :param on_doc_selected: callback(doc_id) when user clicks a document
        :param on_new_doc: callback() when user clicks New Document
        """
        super().__init__()

        self.setMinimumWidth(150)
        self.logger = logger
        self.store = store
        self.on_doc_selected = on_doc_selected
        self.on_new_doc = on_new_doc

        layout = QVBoxLayout(self)

        # __document list__
        self.doc_list = QListWidget()
        # ExtendedSelection supports Shift-range and Ctrl-toggle behavior
        self.doc_list.setSelectionMode(QListWidget.ExtendedSelection)  # multi-select
        self.doc_list.itemClicked.connect(self.handle_doc_click)
        layout.addWidget(self.doc_list)

        # --buttons--
        button_layout = QHBoxLayout()

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_document)
        button_layout.addWidget(self.delete_btn)

        self.merge_btn = QPushButton("Merge")
        self.merge_btn.clicked.connect(self.handle_merge)
        button_layout.addWidget(self.merge_btn)

        layout.addLayout(button_layout)

        self.refresh_list()

        self.logger.debug("FileModule initialized and mounted.")
        # methods

    def refresh_list(self):
        """Reload the list from storage."""
        self.doc_list.clear()
        for doc_id, meta in self.store.index.items():
            title = meta.get("title", "(untitled)")
            item = QListWidgetItem(f"{title} ({doc_id[:8]})")
            item.setData(Qt.UserRole, doc_id)
            self.doc_list.addItem(item)

    def handle_doc_click(self, item):
        """
        If the user clicked without holding Shift/Ctrl/Meta, collapse any multi-selection
        to just the clicked item so a single click always loads that file immediately.
        If a modifier is held, preserve multi-selection behavior.
        """
        modifiers = QApplication.keyboardModifiers()
        multi_key_pressed = bool(
            modifiers & (Qt.ShiftModifier | Qt.ControlModifier | Qt.MetaModifier)
        )
        # if no modifier and there are multiple items selected, restrict to the clicked one
        if not multi_key_pressed and len(self.doc_list.selectedItems()) > 1:
            target_id = item.data(Qt.UserRole)
            # block signals so re-selecting doesn't re-enter this handler
            self.doc_list.blockSignals(True)
            for i in range(self.doc_list.count()):
                list_item = self.doc_list.item(i)
                list_item.setSelected(list_item.data(Qt.UserRole) == target_id)
            self.doc_list.blockSignals(False)
        # only call on_doc_selected when exactly one item is selected
        if self.on_doc_selected and len(self.doc_list.selectedItems()) == 1:
            self.on_doc_selected(item.data(Qt.UserRole))

    def new_document(self):
        if self.on_new_doc:
            self.on_new_doc()
        self.doc_list.clearSelection()

    def delete_document(self):
        """Deletes selected document with confirmation."""
        item = self.doc_list.currentItem()
        if not item:
            return

        doc_id = item.data(Qt.UserRole)
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

    def handle_merge(self):
        """Emit selected document IDs for merging."""
        selected_items = self.doc_list.selectedItems()
        if len(selected_items) < 2:
            QMessageBox.warning(
                self, "Merge Error", "Select at least 2 documents to merge."
            )
            return

        doc_ids = [item.data(Qt.UserRole) for item in selected_items]
        self.merge_signal.emit(doc_ids)
