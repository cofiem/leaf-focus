from pathlib import Path


from leaf_focus.components.pdf.text import Text
from leaf_focus.pipeline.app import app


class PdfTextTask(app.Task):

    name = "leaf-focus.pdf.text"

    def run(self, exe_file: str, pdf_file: str, text_file: str):
        text = Text(Path(exe_file))
        text.create(Path(pdf_file), Path(text_file))
