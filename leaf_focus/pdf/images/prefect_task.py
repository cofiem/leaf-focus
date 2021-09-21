from pathlib import Path
from typing import Iterable

from prefect import Task

from leaf_focus.pdf.identify.item import Item as PdfIdentifyItem
from leaf_focus.pdf.images.operation import Operation


class PrefectTask(Task):
    """A Prefect task to run the pdf images operation."""

    def __init__(self, base_path: Path, exe_path: Path, **kwargs):
        super().__init__(**kwargs)
        self._operation = Operation(self.logger, base_path, exe_path)

    # noinspection PyMethodOverriding
    def run(self, input_item: PdfIdentifyItem) -> Iterable[tuple[str, int]]:
        """Run the task."""
        pdf_path = input_item.pdf_file
        file_hash = input_item.file_hash
        self._operation.run(pdf_path, file_hash)
        for page, _ in self._operation.read(file_hash):
            yield file_hash, page
