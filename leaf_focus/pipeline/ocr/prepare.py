import typing

from leaf_focus.pipeline.app import app

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.ocr.prepare")
def ocr_prepare(self: "Task", file_hash: str, name: str, page: int, threshold: int):

    from leaf_focus.operations.ocr.prepare import Prepare
    from leaf_focus.pipeline.app import logger, config

    prepare = Prepare(logger, config)
    image_path = prepare.run(file_hash, name, page, threshold)
    return str(image_path)
