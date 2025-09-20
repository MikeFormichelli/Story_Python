from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QTextCursor, QTextDocument


class SearchBar(QHBoxLayout):
    def __init__(self, textEditor=None, doc_id=None):
        super().__init__()

        self.textEditor = textEditor
        self.doc_id = doc_id

        # track last search
        self._last_search = ""

        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.find_text)
        self.search_bar.focusInEvent = self.clear_on_focus
        self.addWidget(QLabel("Search:"))
        self.addWidget(self.search_bar)

        search_button = QPushButton("Next")
        search_button.clicked.connect(self.find_text)
        self.addWidget(search_button)

        prev_search_button = QPushButton("Prev")
        prev_search_button.clicked.connect(self.find_previous)
        self.addWidget(prev_search_button)

        clear_button = QPushButton("Clr")
        clear_button.clicked.connect(self.clear_search)
        self.addWidget(clear_button)

    def find_text(self):
        """Find next occurrance of search term."""
        self._find(direction=QTextDocument.FindFlag(0))

    def find_previous(self):
        """Find previous occurance of search term."""
        self._find(direction=QTextDocument.FindBackward)

    def _find(self, direction=QTextDocument.FindFlag(0)):
        if not self.doc_id:
            return

        search_term = self.search_bar.text()
        if not search_term:
            return

        document = self.textEditor.document()
        tc = self.textEditor.textCursor()

        # if new term, start fresh from top or bottom
        if self._last_search != search_term:
            start_pos = (
                document.characterCount() - 1
                if direction == QTextDocument.FindBackward
                else 0
            )
            self._last_search = search_term
        else:
            # ✅ correct way to choose start position
            if direction == QTextDocument.FindBackward:
                start_pos = tc.selectionStart()
            else:
                start_pos = tc.selectionEnd()

        # create a cursor positioned at start_pos and search from there
        start_cursor = QTextCursor(document)
        start_cursor.setPosition(start_pos)

        found_cursor = document.find(search_term, start_cursor, direction)

        if not found_cursor.isNull():
            self.textEditor.setTextCursor(found_cursor)
            self.textEditor.ensureCursorVisible()
            self.textEditor.setFocus()
            return

        # wrap around and try again
        if direction == QTextDocument.FindBackward:
            start_cursor.setPosition(document.characterCount() - 1)
        else:
            start_cursor.setPosition(0)

        found_cursor = document.find(search_term, start_cursor, direction)

        if not found_cursor.isNull():
            self.textEditor.setTextCursor(found_cursor)
            self.textEditor.ensureCursorVisible()
            self.textEditor.setFocus()
            return

        self.search_bar.clear()
        self.search_bar.setText("Term not found.")

    def clear_on_focus(self, event):
        self.search_bar.clear()
        self._last_search = ""
        QLineEdit.focusInEvent(self.search_bar, event)

    def clear_search(self):
        self.search_bar.clear()
        self._last_search = ""
