from pathlib import Path

import typing

from leaf_focus.pipeline.app import app, logger, config

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.pdf.info")
def pdf_info(self: "Task", pdf_identify_file: str):

    self.update_state(
        state="LF_EXTRACTING_PDF_INFO", meta={"input_path": pdf_identify_file}
    )

    from leaf_focus.operations.pdf.info import Info

    input_file = Path(pdf_identify_file)

    info = Info(logger, config)
    pdf_info_file = info.run(input_file)

    self.update_state(
        state="LF_EXTRACTED_PDF_INFO",
        meta={"input_path": pdf_identify_file, "output_path": str(pdf_info_file)},
    )

    return pdf_identify_file
