from pathlib import Path

from leaf_focus.pipeline.app import app, logger, config


@app.task(bind=True, name="leaf-focus.pdf.info")
def pdf_info(self, pdf_identify_file: str):

    from leaf_focus.operations.pdf.info import Info

    input_file = Path(pdf_identify_file)

    info = Info(logger, config)
    info.run(input_file)

    return pdf_identify_file
