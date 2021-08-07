from pathlib import Path


from leaf_focus.components.pdf.images import Images
from leaf_focus.pipeline.app import app


class PdfImagesTask(app.Task):

    name = "leaf-focus.pdf.images"

    def run(self, exe_file: str, pdf_file: str, output_dir: str, prefix: str):
        images = Images(Path(exe_file))
        images.create(Path(pdf_file), Path(output_dir), prefix)
