import typing
from pathlib import Path

from leaf_focus.pipeline.app import app, logger, config

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.ocr.recognise")
def ocr_recognise(self: "Task", pdf_identify_file: str, threshold: int, page: int):

    self.update_state(
        state="LF_CREATING_OCR",
        meta={"input_path": pdf_identify_file, "threshold": threshold, "page": page},
    )

    from leaf_focus.operations.ocr.recognise import Recognise

    input_file = Path(pdf_identify_file)

    recognise = Recognise(logger, config)
    annotation_file, predictions_file = recognise.run(input_file, threshold, page)

    self.update_state(
        state="LF_CREATED_IMAGE",
        meta={
            "input_path": pdf_identify_file,
            "threshold": threshold,
            "page": page,
            "annotated_image_path": str(annotation_file),
            "predictions_path": str(predictions_file),
        },
    )

    return pdf_identify_file
