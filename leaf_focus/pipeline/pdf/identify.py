import typing
from pathlib import Path
from celery import group

from leaf_focus.operations.pdf.identify import Identify
from leaf_focus.pipeline.app import app, logger, config

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.store.identify")
def pdf_identify(self: "Task", details_file: str, base_dir: str):

    self.update_state(
        state="LF_IDENTIFYING_PDF",
        meta={"details_path": details_file, "base_path": base_dir},
    )

    from leaf_focus.pipeline.pdf.info import pdf_info
    from leaf_focus.pipeline.pdf.text import pdf_text
    from leaf_focus.pipeline.pdf.images import pdf_images

    df = Path(details_file)
    bs = Path(base_dir)

    identify = Identify(logger, config)
    pdf_identify_file = identify.run(df, bs)

    self.update_state(
        state="LF_IDENTIFIED_PDF",
        meta={
            "details_path": details_file,
            "base_path": base_dir,
            "identify_path": pdf_identify_file,
        },
    )

    # call the pdf info, text, images tasks
    group(
        pdf_info.si(pdf_identify_file),
        pdf_text.si(pdf_identify_file),
        pdf_images.si(pdf_identify_file),
    ).delay()

    return str(pdf_identify_file)
