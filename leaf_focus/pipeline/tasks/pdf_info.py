from pathlib import Path


from leaf_focus.components.pdf.info import Info
from leaf_focus.pipeline.app import app


class PdfInfoTask(app.Task):

    name = "leaf-focus.pdf.info"

    def run(self, exe_file: str, pdf_file: str, info_file: str):
        info = Info(Path(exe_file))
        info.create(Path(pdf_file), Path(info_file))
