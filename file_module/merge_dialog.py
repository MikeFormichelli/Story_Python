from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QHBoxLayout,
    QDialogButtonBox,
)


class MergeDialog(QDialog):
    def __init__(self, doc_ids, store, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Order Documents for Merge")
        self.doc_ids = doc_ids
        self.store = store

        layout = QVBoxLayout(self)

        # list to order
        self.order_list = QListWidget()
        for doc_id in self.doc_ids:
            title = self.store.index.get(doc_id, {}).get("title", "(untitled)")
            self.order_list.addItem(f"{title} ({doc_id[:8]})")
        layout.addWidget(self.order_list)

        # buttons
        btn_layout = QHBoxLayout()
        up_btn = QPushButton("Up")
        down_btn = QPushButton("Down")
        btn_layout.addWidget(up_btn)
        btn_layout.addWidget(down_btn)

        up_btn.clicked.connect(self.move_up)
        down_btn.clicked.connect(self.move_down)
        layout.addLayout(btn_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def move_up(self):
        row = self.order_list.currentRow()
        if row > 0:
            item = self.order_list.takeItem(row)
            self.order_list.insertItem(row - 1, item)
            self.order_list.setCurrentRow(row - 1)

    def move_down(self):
        row = self.order_list.currentRow()
        if row < self.order_list.count() - 1:
            item = self.order_list.takeItem(row)
            self.order_list.insertItem(row + 1, item)
            self.order_list.setCurrentRow(row + 1)

    def ordered_doc_ids(self):
        """Return doc_ids in user-selected order"""
        ordered = []
        for i in range(self.order_list.count()):
            # find original doc_id by matching displayed title snippet
            text = self.order_list.item(i).text()
            for doc_id in self.doc_ids:
                if doc_id[:8] in text:
                    ordered.append(doc_id)
                    break
        return ordered
