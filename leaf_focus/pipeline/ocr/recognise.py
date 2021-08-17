from pathlib import Path

from leaf_focus.pipeline.app import app, logger, config


@app.task(bind=True, name="leaf-focus.ocr.recognise")
def ocr_recognise(self, pdf_identify_file: str, threshold: int, page: int):

    from leaf_focus.operations.ocr.recognise import Recognise

    input_file = Path(pdf_identify_file)
    recognise = Recognise(logger, config)
    recognise.run(input_file, threshold, page)

    return pdf_identify_file
