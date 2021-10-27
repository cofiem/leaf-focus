from pathlib import Path

from prefect import Task

from leaf_focus.download.crawl.item import Item as DownloadCrawlItem
from leaf_focus.pdf.identify.item import Item as PdfIdentifyItem
from leaf_focus.pdf.identify.operation import Operation


class PdfIdentifyTask(Task):
    """A Prefect task to run the pdf identify operation."""

    def __init__(self, base_path: Path, **kwargs):
        kwargs = {**kwargs, "name": "pdf.identify"}
        super().__init__(**kwargs)
        self._operation = Operation(self.logger, base_path)

    # noinspection PyMethodOverriding
    def run(self, input_item: DownloadCrawlItem) -> PdfIdentifyItem:
        """Run the task."""
        pdf_path = Path(input_item.path)
        pdf_identify_path = self._operation.run(pdf_path)
        output_item = PdfIdentifyItem.read(pdf_identify_path)
        return output_item
