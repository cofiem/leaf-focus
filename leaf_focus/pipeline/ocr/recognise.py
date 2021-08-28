import typing
from pathlib import Path

from leaf_focus.pipeline.app import app, logger, config

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.ocr.recognise")
def ocr_recognise(self: "Task", pdf_identify_file: str, page: int, threshold: int):

    from leaf_focus.operations.ocr.recognise import Recognise

    input_file = Path(pdf_identify_file)

    recognise = Recognise(logger, config)
    recognise.run(input_file, page, threshold)
