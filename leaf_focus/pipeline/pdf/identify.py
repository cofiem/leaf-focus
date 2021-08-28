import typing
from pathlib import Path
from celery import group

from leaf_focus.operations.pdf.identify import Identify
from leaf_focus.pipeline.app import app, logger, config

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.store.identify")
def pdf_identify(self: "Task", details_file: str):

    from leaf_focus.pipeline.pdf.info import pdf_info
    from leaf_focus.pipeline.pdf.text import pdf_text
    from leaf_focus.pipeline.pdf.images import pdf_images

    df = Path(details_file)
    identify = Identify(logger, config)
    pdf_identify_path = identify.run(df)
    pdf_identify_file = str(pdf_identify_path)

    group(pdf_info.s(), pdf_text.s(), pdf_images.s()).delay(pdf_identify_file)
