from pathlib import Path


from leaf_focus.components.ocr.recognise import Recognise
from leaf_focus.pipeline.app import app


class OcrRecogniseTask(app.Task):

    name = "leaf-focus.ocr.recognise"

    def run(self, image_file: str, annotation_file: str, predictions_file: str):
        recognise = Recognise()
        recognise.recognise_text(
            Path(image_file), Path(annotation_file), Path(predictions_file)
        )
