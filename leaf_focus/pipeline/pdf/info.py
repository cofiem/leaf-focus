from pathlib import Path

import typing

from leaf_focus.pipeline.app import app

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.pdf.info")
def pdf_info(self: "Task", pdf_file: str, file_hash: str, name: str):

    from leaf_focus.operations.pdf.info import Info
    from leaf_focus.pipeline.app import logger, config

    info = Info(logger, config)
    pdf_path = Path(pdf_file)
    info_path = info.run(pdf_path, file_hash, name)
    return str(info_path)
