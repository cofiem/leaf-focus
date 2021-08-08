from pathlib import Path

from celery import group

from leaf_focus.pipeline.app import app, operations


@app.task(bind=True, name="leaf-focus.store.identify")
def pdf_identify(self, details_file: str, base_dir: str):
    df = Path(details_file)
    bs = Path(base_dir)
    pdf_identify_file = operations.pdf_identify(df, bs)

    # call the pdf info, text, images tasks
    group(
        pdf_info.si(pdf_identify_file),
        pdf_text.si(pdf_identify_file),
        pdf_images.si(pdf_identify_file),
    ).delay()

    return str(pdf_identify_file)


@app.task(bind=True, name="leaf-focus.pdf.images")
def pdf_images(self, pdf_identify_file: str):
    pdf_image_files = operations.pdf_images(Path(pdf_identify_file))

    # call the ocr prepare tasks
    threshold = operations.image_threshold
    group(
        ocr_prepare.si(str(pdf_identify_file), threshold, page)
        for path, page in pdf_image_files
    ).delay()

    return pdf_identify_file


@app.task(bind=True, name="leaf-focus.pdf.info")
def pdf_info(self, pdf_identify_file: str):
    operations.pdf_info(Path(pdf_identify_file))
    return pdf_identify_file


@app.task(bind=True, name="leaf-focus.pdf.text")
def pdf_text(self, pdf_identify_file: str):
    operations.pdf_text(Path(pdf_identify_file))
    return pdf_identify_file


@app.task(bind=True, name="leaf-focus.ocr.prepare")
def ocr_prepare(self, pdf_identify_file: str, threshold: int, page: int):
    operations.ocr_prepare(Path(pdf_identify_file), threshold, page)

    # call the ocr recognise task
    ocr_recognise.si(str(pdf_identify_file), threshold, page).delay()

    return pdf_identify_file


@app.task(bind=True, name="leaf-focus.ocr.recognise")
def ocr_recognise(self, pdf_identify_file: str, threshold: int, page: int):
    operations.ocr_recognise(Path(pdf_identify_file), threshold, page)
    return pdf_identify_file
