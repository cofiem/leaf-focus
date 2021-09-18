import typing

from leaf_focus.pipeline.app import app

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.ocr.recognise")
def ocr_recognise(self: "Task", file_hash: str, name: str, page: int, threshold: int):

    from leaf_focus.operations.ocr.recognise import Recognise
    from leaf_focus.pipeline.app import logger, config

    recognise = Recognise(logger, config)
    annotation_path, predictions_path = recognise.run(file_hash, name, page, threshold)
    return [str(annotation_path), str(predictions_path)]
