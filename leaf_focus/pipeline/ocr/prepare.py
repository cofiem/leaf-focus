from pathlib import Path

from leaf_focus.pipeline.app import app, logger, config


@app.task(bind=True, name="leaf-focus.ocr.prepare")
def ocr_prepare(self, pdf_identify_file: str, threshold: int, page: int):

    from leaf_focus.operations.ocr.prepare import Prepare
    from leaf_focus.pipeline.ocr.recognise import ocr_recognise

    input_file = Path(pdf_identify_file)

    prepare = Prepare(logger, config)
    prepare.run(input_file, threshold, page)

    # call the ocr recognise task
    ocr_recognise.si(pdf_identify_file, threshold, page).delay()

    return pdf_identify_file
