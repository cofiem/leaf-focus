from pathlib import Path
from celery import group

from leaf_focus.pipeline.app import app, logger, config


@app.task(bind=True, name="leaf-focus.pdf.images")
def pdf_images(self, pdf_identify_file: str):

    from leaf_focus.operations.pdf.images import Images
    from leaf_focus.pipeline.ocr.prepare import ocr_prepare

    input_file = Path(pdf_identify_file)

    images = Images(logger, config)
    pdf_image_files = images.run(input_file)

    # call the ocr prepare tasks
    threshold = config.image_threshold
    group(
        ocr_prepare.si(str(pdf_identify_file), threshold, page)
        for path, page in pdf_image_files
    ).delay()

    return pdf_identify_file
