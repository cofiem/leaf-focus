import typing
from pathlib import Path
from celery import group

from leaf_focus.pipeline.app import app, logger, config

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.pdf.images")
def pdf_images(self: "Task", pdf_identify_file: str):

    self.update_state(
        state="LF_CREATING_PAGE_IMAGES", meta={"input_path": pdf_identify_file}
    )

    from leaf_focus.operations.pdf.images import Images
    from leaf_focus.pipeline.ocr.prepare import ocr_prepare

    input_file = Path(pdf_identify_file)

    images = Images(logger, config)
    pdf_image_paths = images.run(input_file)

    self.update_state(
        state="LF_CREATED_PAGE_IMAGES",
        meta={"input_path": pdf_identify_file, "page_count": len(pdf_image_paths)},
    )

    # call the ocr prepare tasks
    threshold = config.image_threshold

    task_group = []
    for path, page in pdf_image_paths:
        task_group.append(ocr_prepare.si(str(pdf_identify_file), threshold, page))

    group(task_group).delay()

    return pdf_identify_file