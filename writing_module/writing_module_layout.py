from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from .writing_window import WritingModule

# from .row_editor import RowBasedHtmlEditor
# from .html_viewport import HtmlViewer


class WritingLayout(QWidget):
    def __init__(self, store, pdf_generator, logger):
        super().__init__()

        self.setWindowTitle("Writer Layout")
        self.setMinimumSize(600, 800)
        self.store = store
        self.logger = logger

        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # add writing tab
        self.writing_tab = WritingModule(
            store=self.store, pdf_generator=pdf_generator, logger=self.logger
        )
        # writing_sub_layout = QVBoxLayout(writing_tab)
        self.tabs.addTab(self.writing_tab, "Writer")

        # # add editor tab
        # self.editor_tab = RowBasedHtmlEditor()
        # self.tabs.addTab(self.editor_tab, "Editor")

        # html tab
        # self.html_tab = HtmlViewer()
        # self.tabs.addTab(self.html_tab, "HTML View")

        self.logger.debug("Writing layout initialized.")
