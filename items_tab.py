from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QLabel,
    QScrollArea,
    QFormLayout,
    QTableWidgetItem,
    QHeaderView,
)


class ItemsTab(QWidget):
    def __init__(self, items_collection):
        super().__init__()

        self.items_collection = items_collection
        self.layout = QVBoxLayout(self)

        # list of items:
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(2)
        self.items_table.setHorizontalHeaderLabels(["Name", "Type"])
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)  # read-only
        self.items_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.items_table.setSelectionMode(QTableWidget.SingleSelection)
        self.items_table.cellClicked.connect(self.load_selected_item)
        self.layout.addWidget(QLabel("Added Items"))
        self.layout.addWidget(self.items_table)

        # scrollable area for dynamic content
        self.items_detail_scroll = QScrollArea()
        self.items_detail_scroll.setWidgetResizable(True)

        self.item_detail_container = QWidget()
        self.item_detail_layout = QFormLayout()
        self.item_detail_container.setLayout(self.item_detail_layout)

        self.items_detail_scroll.setWidget(self.item_detail_container)
        self.layout.addWidget(self.items_detail_scroll)

        # populate from other collection
        self.load_items_collection()

    def load_items_collection(self):
        self.items = []
        # self.items_list_widget.clear()
        self.items_table.setRowCount(0)

        try:
            cursor = self.items_collection.find()
            self.items = list(cursor)
            self.items_table.setRowCount(len(self.items))

            for row, item in enumerate(self.items):
                name = item.get("name", str(item.get("_id")))
                type_ = item.get("type", "unknown").upper()
                self.items_table.setItem(row, 0, QTableWidgetItem(name))
                self.items_table.setItem(row, 1, QTableWidgetItem(type_))

            header = self.items_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        except Exception as e:
            print("Error loading items:", e)

    def load_selected_item(self, row, column):
        # index = self.items_list_widget.currentRow()
        if 0 <= row < len(self.items):
            selected_item = self.items[row]
            self.display_item_details(selected_item)

    def display_item_details(self, item):
        # clear existing layout
        while self.item_detail_layout.count():
            child = self.item_detail_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # add key-value labels
        for key, value in item.items():
            key_label = QLabel(str(key))
            val_label = QLabel(str(value))
            val_label.setWordWrap(True)
            self.item_detail_layout.addRow(key_label, val_label)
