from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from .writing_window import WritingModule


class WritingLayout(QWidget):
    def __init__(self, store):
        super().__init__()

        self.setWindowTitle("Writer Layout")
        self.setMinimumSize(600, 800)
        self.store = store

        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # add writing tab
        self.writing_tab = WritingModule(store=self.store)
        # writing_sub_layout = QVBoxLayout(writing_tab)
        self.tabs.addTab(self.writing_tab, "Writer")
