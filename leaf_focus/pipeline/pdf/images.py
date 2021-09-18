import typing
from pathlib import Path
from leaf_focus.pipeline.app import app

if typing.TYPE_CHECKING:
    from celery import Task


@app.task(bind=True, name="leaf-focus.pdf.images")
def pdf_images(self: "Task", pdf_file: str, file_hash: str, name: str):

    from leaf_focus.pipeline.app import logger, config
    from leaf_focus.operations.pdf.images import Images

    pdf_path = Path(pdf_file)

    images = Images(logger, config)
    pdf_image_paths = images.run(pdf_path, file_hash, name)
    return [{"path": str(p), "page": n} for p, n in pdf_image_paths]
