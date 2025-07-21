from PySide6 import QtWidgets


class ShowWidget(QtWidgets.QWidget):
    def __init__(self, data=None):
        super().__init__()

        self.setWindowTitle("Character Viewer")
        self.setFixedSize(400, 600)

        # scrollable area:
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)

        # create a widget to hold the layout contents
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background-color: #2a2a2a")
        layout = QtWidgets.QVBoxLayout(content_widget)

        if data:
            for key, value in data.items():
                label = QtWidgets.QLabel(
                    f"<span style='font-size:12pt; color:#08B7F4;'><b>{key.upper()}:</b></span> <span style='font-size:11pt; color:#F5F7F2;'>{value}</span>"
                )
                label.setWordWrap(True)  # word wrap for long text
                layout.addWidget(label)
        else:
            label = QtWidgets.QLabel("No data loaded.")
            label.setWordWrap(True)
            layout.addWidget(label)

        scroll_area.setWidget(content_widget)

        # add the scroll area to the main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
