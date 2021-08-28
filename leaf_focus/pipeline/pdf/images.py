import typing
from pathlib import Path
from celery import group
from leaf_focus.pipeline.app import app, logger, config

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.pdf.images")
def pdf_images(self: "Task", pdf_identify_file: str):

    from leaf_focus.operations.pdf.images import Images
    from leaf_focus.pipeline.ocr.prepare import ocr_prepare

    input_file = Path(pdf_identify_file)
    images = Images(logger, config)
    pdf_image_paths = images.run(input_file)

    threshold = config.image_threshold
    group(
        ocr_prepare.si(pdf_identify_file, page, threshold)
        for path, page in pdf_image_paths
    ).delay()
