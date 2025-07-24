from PySide6 import QtWidgets, QtCore
import sys

class CharacterWidget(QtWidgets.QWidget):
    def __init__(self, data=None):
        super().__init__()
        self.data = data

        field_list = []

        self.setWindowTitle("Test Character Viewer")
        self.setFixedSize(400, 600)
        
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.activateWindow()
        self.raise_()
        
        # scrollable area:
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)

        # create a widget to hold the layout contents
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background-color: #2a2a2a")
        layout = QtWidgets.QVBoxLayout(content_widget)

        if data:
            for key, value in data.items():
                if key not in ["store", "_id"]:
                    label = QtWidgets.QLabel(
                        f"<span style='font-size:12pt; color:#08B7F4;'><b>{key.upper()}:</b></span> <span style='font-size:11pt; color:#F5F7F2;'>{value}</span>"
                    )
                    label.setWordWrap(True)  # word wrap for long text
                    # layout.addWidget(label)
                    field_list.append(label)
        else:
            label = QtWidgets.QLabel("No data loaded.")
            label.setWordWrap(True)
            layout.addWidget(label)

        for item in field_list:
                layout.addWidget(item)
                
        scroll_area.setWidget(content_widget)

        # add the scroll area to the main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(scroll_area)

        #button

        def clicked_button(text):
            for item in field_list:
                layout.addWidget(item)

        switch_button = QtWidgets.QPushButton("Switch Mode")
        switch_button.setStyleSheet("background-color: #fff; color: #c6c6ff;")
        

        #input experiment
        input_wid = QtWidgets.QLineEdit()
        input_wid.setStyleSheet("background-color:#fff;")
        layout.addWidget(input_wid)
        
        switch_button.clicked.connect(lambda: clicked_button(input_wid.text()))
        layout.addWidget(switch_button)

app = QtWidgets.QApplication(sys.argv)
widget = CharacterWidget(data={"Test": "Test line one.", "Test2": "Testline two", "field 3": "why not have a field three!!!!"})
widget.show()
sys.exit(app.exec())