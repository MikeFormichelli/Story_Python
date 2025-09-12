from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Signal, Qt


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
