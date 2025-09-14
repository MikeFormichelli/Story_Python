from PySide6.QtWidgets import (
    QTextEdit,
)

from PySide6.QtGui import (
    QTextCharFormat,
    QFont,
    QTextCursor,
    QPixmap,
)

from PySide6.QtCore import Qt


class IndentedTextEdit(QTextEdit):
    def __init__(self, font_selector=None, font_size_combo=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.font_selector = font_selector
        self.font_size_combo = font_size_combo

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            cursor = self.textCursor()

            # Determine whterh the current (previous) block is a heading
            try:
                prev_block = cursor.block()
                prev_block_fmt = prev_block.blockFormat()
                prev_heading = prev_block_fmt.headingLeve()  # int, 0 if not a heading
            except Exception:
                prev_heading = 0

            # Get current line text
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            line_text = cursor.selectedText()

            # Count leading spaces/tabs for previous line
            leading_whitespace = ""
            for ch in line_text:
                if ch in (" ", "\t"):
                    leading_whitespace += ch
                else:
                    break

            # If line has no leading whitespace, use default indent
            indent = leading_whitespace or "    "

            # Let QTextEdit handle the newline first
            super().keyPressEvent(event)

            if self.font_selector and self.font_size_combo:

                if hasattr(self.parent(), "set_editor_font"):
                    self.parent().set_editor_font()  # make sure parent has this method
                else:
                    normal_fmt = QTextCharFormat()
                    normal_fmt.setFontFamily(self.font_selector.currentText())
                    normal_fmt.setFontPointSize(
                        float(self.font_size_combo.currentText())
                    )
                    normal_fmt.setFontWeight(QFont.Weight.Normal)
                    self.mergeCurrentCharFormat(normal_fmt)
                    self.setCurrentFont(
                        QFont(self.font_selector.currentText())
                    )  # <-- key bit!

                    # Insert the indent
                    self.insertPlainText(indent)

        else:
            super().keyPressEvent(event)

    def insert_image(self, image_path, align="left", max_ratio=0.3):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return

        max_width = int(self.viewport().width() * max_ratio)
        scaled_pixmap = pixmap.scaledToWidth(max_width, Qt.SmoothTransformation)

        img_width = scaled_pixmap.width()
        img_height = scaled_pixmap.height()

        image_html = (
            f'<img src="{image_path}" '
            f'width="{img_width}" height="{img_height}" '
            f'style="float:{align}; margin: 5px;" />'
        )

        cursor = self.textCursor()
        cursor.insertHtml(image_html)
        cursor.insertHtml("<br>")  # ensures the cursor goes below image
        self.ensureCursorVisible()

        # Reapply font/size to the new block
        if self.font_selector and self.font_size_combo:
            normal_fmt = QTextCharFormat()
            normal_fmt.setFontFamily(self.font_selector.currentText())
            normal_fmt.setFontPointSize(float(self.font_size_combo.currentText()))
            normal_fmt.setFontWeight(QFont.Weight.Normal)
            self.mergeCurrentCharFormat(normal_fmt)
            self.setCurrentFont(QFont(self.font_selector.currentText()))
