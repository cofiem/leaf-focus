import typing
from pathlib import Path

from leaf_focus.pipeline.app import app, logger, config

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.ocr.prepare")
def ocr_prepare(self: "Task", pdf_identify_file: str, threshold: int, page: int):

    self.update_state(
        state="LF_PREPARING_IMAGE",
        meta={"input_path": pdf_identify_file, "threshold": threshold, "page": page},
    )

    from leaf_focus.operations.ocr.prepare import Prepare
    from leaf_focus.pipeline.ocr.recognise import ocr_recognise

    input_file = Path(pdf_identify_file)

    prepare = Prepare(logger, config)
    prepared_image = prepare.run(input_file, threshold, page)

    self.update_state(
        state="LF_PREPARED_IMAGE",
        meta={
            "input_path": pdf_identify_file,
            "threshold": threshold,
            "page": page,
            "output_path": str(prepared_image),
        },
    )

    # call the ocr recognise task
    ocr_recognise.si(pdf_identify_file, threshold, page).delay()

    return pdf_identify_file
