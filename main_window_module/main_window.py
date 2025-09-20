import os
import uuid
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QApplication, QDialog

from PySide6.QtCore import Qt

import fitz

from character_module import CharacterApp

from writing_module import WritingStore, WritingLayout

from file_module import FileModule, MergeDialog

from output_module import PDFGenerator


class MainWindow(QWidget):
    def __init__(self, logger):
        super().__init__()
        self.setWindowTitle("Character Record & Story App")
        self.setMinimumSize(1530, 815)

        # logger
        self.logger = logger

        # store for writer
        self.store = WritingStore(logger=self.logger)

        self.pdf_generator = PDFGenerator(logger=self.logger)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        character_pane = CharacterApp(
            pdf_generator=self.pdf_generator,
            logger=self.logger,
            html_saver=self.store.save_document,
        )
        splitter.addWidget(character_pane)

        self.writing_pane = WritingLayout(
            store=self.store, pdf_generator=self.pdf_generator, logger=self.logger
        )
        splitter.addWidget(self.writing_pane)

        self.file_pane = FileModule(
            store=self.store,
            on_doc_selected=self.load_document,
            on_new_doc=self.create_new_document,
            logger=self.logger,
        )
        splitter.addWidget(self.file_pane)

        # ✅ Connect the signal from WritingModule to refresh file list
        self.writing_pane.writing_tab.document_saved.connect(
            self.file_pane.refresh_list
        )
        self.file_pane.delete_signal.connect(
            self.writing_pane.writing_tab.create_new_doc
        )
        character_pane.save_html_signal.connect(self.file_pane.refresh_list)

        # connect the file_pane signal for merge
        self.file_pane.merge_signal.connect(self.merge_documents)

        layout = QVBoxLayout(self)
        layout.addWidget(splitter)

        # ---- center on screen ----
        self.center_on_screen()

        self.logger.info("Main Window booted & mounted")

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
        store = WritingStore(logger=self.logger)
        html = store.get_document(doc_id)
        meta = store.index.get(doc_id, {})
        self.writing_pane.writing_tab.doc_id = doc_id
        self.writing_pane.writing_tab.textEditSpace.setHtml(html or "")
        self.writing_pane.writing_tab.title_input.setText(meta.get("title", ""))
        self.writing_pane.writing_tab.load_font_and_size(
            meta.get("font", "Garamond"), meta.get("font_size", "12")
        )

    def create_new_document(self):
        """Called when FileModule creates a new doc."""
        self.writing_pane.writing_tab.create_new_document()

    def merge_documents(self, doc_ids):
        dialog = MergeDialog(doc_ids, self.store, self)
        if dialog.exec() == QDialog.Accepted:
            ordered_ids = dialog.ordered_doc_ids()
            merged_html = ""

            for doc_id in ordered_ids:
                html = self.store.get_document(doc_id)
                merged_html += (
                    "<div>" + html + "</div>" + '<hr style="margin: 20px 0";>'
                )  # simple divider

            # ✅ handle merging external PDFs
            # outputs_dir = os.path.join(self.store.base_dir, "outputs")
            # for doc_id in ordered_ids:
            #     meta = self.store.index.get(doc_id)
            #     if meta and meta.get("pdf_filename"):
            #         pdf_path = os.path.join(outputs_dir, meta["pdf_filename"])
            #         html_from_pdf = self.pdf_to_html(pdf_path)
            #         merged_html += html_from_pdf + "<hr>"

            # ✅ save as new HTML document
            new_id = str(uuid.uuid4())
            first_doc_meta = self.store.index.get(ordered_ids[0], {})
            font = first_doc_meta.get("font", "Garamond")
            font_size = first_doc_meta.get("font_size", "12")

            self.store.save_document(
                new_id,
                merged_html,
                title="Merged Document",
                font=font,
                font_size=font_size,
            )
            self.logger.info(f"Merged {len(ordered_ids)} docs into {new_id}")
            self.load_document(new_id)
            self.file_pane.refresh_list()

    def pdf_to_html(self, pdf_path):
        """Convert a PDF file to HTML string (simplest approach)"""

        try:
            doc = fitz.open(pdf_path)
            html = ""
            for page in doc:
                html += page.get_text("html")
            return html
        except ImportError:
            self.logger.error("PyMuPDF not installed. PDF to HTML skipped.")
            return "<p>[PDF could not be converted to HTML]</p>"
