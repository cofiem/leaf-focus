import typing
from pathlib import Path

from leaf_focus.pipeline.app import app

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.pdf.text")
def pdf_text(self: "Task", pdf_file: str, file_hash: str, name: str):

    from leaf_focus.pipeline.app import logger, config
    from leaf_focus.operations.pdf.text import Text

    pdf_path = Path(pdf_file)
    text = Text(logger, config)
    text_path = text.run(pdf_path, file_hash, name)
    return str(text_path)
