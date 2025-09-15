from pathlib import Path
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from bs4 import BeautifulSoup
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QSizePolicy
from PySide6.QtCore import QUrl


class PDFGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent  # folder containing this file
        env = Environment(loader=FileSystemLoader(self.base_dir / "templates"))
        self.template = env.get_template("template.html")
        self.css_file = self.base_dir / "style.css"

    # methods:

    def run_generator(self, html_path, output_path, extra_styles=None):
        print("pdf generator running")

        html_file = self.base_dir.parent / "data" / "html" / html_path
        output_file = self.base_dir.parent / "outputs" / f"{output_path}.pdf"

        # read the HTML content
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        fixed_html_dict = self.soup_parser(html_string=html_content)
        fixed_html = fixed_html_dict["fixed_html"]

        # build stylesheet
        stylesheets = [CSS(filename=str(self.css_file))]
        if extra_styles:
            stylesheets.append(CSS(string=extra_styles))  # overrides last

        # preview
        self.preview_html(fixed_html=fixed_html)

        # generate PDF:
        HTML(string=fixed_html).write_pdf(str(output_file), stylesheets=stylesheets)

        print("PDF generator finished")

    def generate_character_sheet(self, data_dict):
        print("Starting pdf generation")

        # # check output dir:
        output_dir = self.base_dir.parent / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Make sure image path is absolute
        if "image_path" in data_dict:
            data_dict["image_path"] = Path(data_dict["image_path"]).resolve().as_uri()
            print(f"Using image: {data_dict['image_path']}")

        if "cyberware" in data_dict:
            print(data_dict["cyberware"])
            cyberware_list = data_dict["cyberware"]
            rows = []
            for i in range(0, len(cyberware_list), 4):
                rows.append(cyberware_list[i : i + 4])
            data_dict["cyberware"] = rows
            print(data_dict["cyberware"])

        rendered_output = self.template.render(data_dict)
        # print(rendered_output)

        output_file = self.base_dir.parent / "outputs" / f"{data_dict['handle']}.pdf"

        # Tell WeasyPrint where to resolve relative paths from (very important!)
        HTML(string=rendered_output, base_url=data_dict["image_path"]).write_pdf(
            target=str(output_file), stylesheets=[CSS(filename=str(self.css_file))]
        )

        print(f"PDF generated at {output_file}")

        return output_file

    def preview_html(self, fixed_html: str):
        """Show preview popup of HTML before generating PDF"""

        dlg = QDialog(None)
        dlg.setWindowTitle("Preview")
        dlg.resize(1000, 800)

        layout = QVBoxLayout()

        # web view to render the html
        webview = QWebEngineView(dlg)
        webview.setHtml(fixed_html, QUrl.fromLocalFile(str(self.base_dir.parent)))
        webview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(webview)

        # close button
        close_btn = QPushButton("CLose", dlg)
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.setLayout(layout)

        dlg.exec()

    def soup_parser(self, html_string: str, extra_styles: str | None = None) -> dict:
        """Process HTML: fix image paths, add classes, and prepare head for CSS."""

        # convert all <img> src paths to file:// URIs
        soup = BeautifulSoup(html_string, "html.parser")

        for img in soup.find_all("img"):
            img_path = Path(img["src"]).resolve()
            img["src"] = img_path.as_uri()

            # add class for styling
            existing_classes = img.get("class", [])
            if isinstance(existing_classes, str):  # just in case it's a string
                existing_classes = existing_classes.split()
            if "pdf-img" not in existing_classes:
                existing_classes.append("pdf-img")
            if "float" not in existing_classes:
                float_dir = img.get("style", "").split(":")[1].strip()
                if float_dir == "right;":
                    existing_classes.append("float-right")
                elif float_dir == "left;":
                    existing_classes.append("float-left")
            img["class"] = existing_classes

        # prep head
        head = soup.head or soup.new_tag("head")

        # link to css
        link_main = soup.new_tag(
            "link", rel="stylesheet", href=self.css_file.resolve().as_uri()
        )
        head.append(link_main)

        # inject extra styles
        if extra_styles:
            style_tag = soup.new_tag("style")
            style_tag.string = extra_styles
            head.append(style_tag)

        # ensure head is in soup
        if not soup.head:
            soup.html.insert(0, head)

        # convert back to string:
        return {"fixed_html": str(soup), "head": head}
