import os
import json
from datetime import datetime


class WritingStore:
    """
    Simple writing store that saves text files and metadata locally.
    Can be swapped later for MongoDB or SQLite by reimplementing methods.
    """

    def __init__(
        self, base_dir=None, html_subdir="html", index_file="index.json", logger=None
    ):

        # set logger
        logger = logger

        if base_dir is None:
            logger.debug("base_dir is None. Setting current_dir and base_dir.")

            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.join(current_dir, "..", "data")

        self.base_dir = os.path.abspath(base_dir)  # normalize path
        self.html_dir = os.path.join(self.base_dir, html_subdir)
        self.index_file = os.path.join(self.base_dir, index_file)
        self.index = {}

        # ensure directories exist
        os.makedirs(self.html_dir, exist_ok=True)

        logger.debug("Directories ensured.")

        self.load_index()

        logger.debug("Index loaded")

    def load_index(self):
        if os.path.exists(self.index_file):
            with open(self.index_file, "r", encoding="utf-8") as f:
                self.index = json.load(f)
        else:
            self.index = {}

    def list_documents(self):
        """Return a list of document metadata (title, file, last_modified)"""
        return list(self.index.values())

    def get_document(self, doc_id):
        """Return saved html content for given doc_id, or empty string if missing"""
        meta = self.index.get(doc_id)
        if not meta:
            return ""

        file_path = os.path.join(self.html_dir, meta["filename"])
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def save_document(
        self, doc_id, html_content, title=None, font=None, font_size=None
    ):
        """Save HTML content to its own file and update index."""
        file_name = f"{doc_id}.html"
        file_path = os.path.join(self.html_dir, file_name)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.index[doc_id] = {
            "filename": file_name,
            "font": font,
            "font_size": font_size,
            "title": title or self.index.get(doc_id, {}).get("title", ""),
            "last_modified": datetime.now().isoformat(),
        }
        self._save_index()

    def delete_document(self, doc_id):
        """Delete a document and its metadata."""
        meta = self.index.pop(doc_id, None)
        if meta:
            file_path = os.path.join(self.html_dir, meta["filename"])
            if os.path.exists(file_path):
                os.remove(file_path)
            self._save_index()

    def _save_index(self):
        """write index to disk"""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
