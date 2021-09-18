import typing
from pathlib import Path

from leaf_focus.operations.pdf.identify import Identify
from leaf_focus.pipeline.app import app, logger, config

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.store.identify")
def pdf_identify(self: "Task", pdf_file: str, name: str):

    pdf_path = Path(pdf_file)
    identify = Identify(logger, config)
    pdf_identify_path = identify.run(pdf_path, name)
    return str(pdf_identify_path)
