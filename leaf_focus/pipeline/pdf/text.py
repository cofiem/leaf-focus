from pathlib import Path

from leaf_focus.pipeline.app import app, logger, config


@app.task(bind=True, name="leaf-focus.pdf.text")
def pdf_text(self, pdf_identify_file: str):

    from leaf_focus.operations.pdf.text import Text

    input_file = Path(pdf_identify_file)

    text = Text(logger, config)
    text.run(input_file)

    return pdf_identify_file
