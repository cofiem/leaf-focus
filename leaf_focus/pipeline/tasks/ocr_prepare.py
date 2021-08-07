from pathlib import Path

from leaf_focus.components.ocr.prepare import Prepare
from leaf_focus.pipeline.app import app


class OcrPrepareTask(app.Task):

    name = "leaf-focus.ocr.prepare"

    def run(self, input_file: str, threshold_file: str, threshold: int):
        prepare = Prepare()
        prepare.threshold(Path(input_file), Path(threshold_file), threshold)
