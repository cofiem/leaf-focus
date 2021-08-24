import typing
from pathlib import Path

from leaf_focus.pipeline.app import app, logger, config

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.pdf.text")
def pdf_text(self: "Task", pdf_identify_file: str):

    self.update_state(
        state="LF_EXTRACTING_PDF_TEXT", meta={"input_path": pdf_identify_file}
    )

    from leaf_focus.operations.pdf.text import Text

    input_file = Path(pdf_identify_file)

    text = Text(logger, config)
    pdf_text_path = text.run(input_file)
    pdf_text_file = str(pdf_text_path)

    self.update_state(
        state="LF_EXTRACTING_PDF_TEXT",
        meta={"input_path": pdf_identify_file, "output_path": pdf_text_file},
    )

    return pdf_identify_file
