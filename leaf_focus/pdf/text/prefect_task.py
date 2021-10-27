from pathlib import Path
from prefect import Task

from leaf_focus.pdf.identify.item import Item as PdfIdentifyItem
from leaf_focus.pdf.text.operation import Operation


class PdfTextTask(Task):
    """A Prefect task to run the pdf text operation."""

    def __init__(self, base_path: Path, exe_path: Path, **kwargs):
        kwargs = {**kwargs, "name": "pdf.text"}
        super().__init__(**kwargs)
        self._operation = Operation(self.logger, base_path, exe_path)

    # noinspection PyMethodOverriding
    def run(self, input_item: PdfIdentifyItem) -> list[list[str]]:
        """Run the task."""
        pdf_path = input_item.pdf_file
        text_path = self._operation.run(pdf_path, input_item.file_hash)
        output_item = self._operation.read(text_path)
        return output_item
