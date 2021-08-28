import typing
from pathlib import Path

from leaf_focus.pipeline.app import app, logger, config

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.ocr.prepare")
def ocr_prepare(self: "Task", pdf_identify_file: str, page: int, threshold: int):

    from leaf_focus.operations.ocr.prepare import Prepare
    from leaf_focus.pipeline.ocr.recognise import ocr_recognise

    input_file = Path(pdf_identify_file)

    prepare = Prepare(logger, config)
    prepare.run(input_file, page, threshold)

    ocr_recognise.si(pdf_identify_file, page, threshold).delay()
