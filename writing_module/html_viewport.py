from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl


class HtmlViewer(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.loadFinished.connect(self.on_load_finished)

        with open(
            r"C:\Users\Mike\Dropbox\repos\Story_Python\data\html\22f0d588-c158-4b21-967b-3775810686fe.html",
            "r",
            encoding="utf-8",
        ) as f:
            html = f.read()
            self.load_html(html)

    def load_html(self, html, base_url=None):
        if base_url:
            self.setHtml(html, QUrl.fromLocalFile(str(base_url)))
        else:
            self.setHtml(html)

    # def on_load_finished(self, ok):
    #     if ok:
    #         # Execute JavaScript to change the content of the editable div
    #         self.page().runJavaScript(
    #             "document.getElementById('editableDiv').innerText = 'Content changed from PySide6!';"
    #         )
