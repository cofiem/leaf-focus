from pathlib import Path
from celery import group

from leaf_focus.pipeline.app import app


@app.task(bind=True, name="leaf-focus.store.identify")
def pdf_identify(self, details_file: str, base_dir: str):

    from leaf_focus.pipeline.pdf.info import pdf_info
    from leaf_focus.pipeline.pdf.text import pdf_text
    from leaf_focus.pipeline.pdf.images import pdf_images

    df = Path(details_file)
    bs = Path(base_dir)
    pdf_identify_file = app.settings.pdf_identify(df, bs)

    # call the pdf info, text, images tasks
    group(
        pdf_info.si(pdf_identify_file),
        pdf_text.si(pdf_identify_file),
        pdf_images.si(pdf_identify_file),
    ).delay()

    return str(pdf_identify_file)
