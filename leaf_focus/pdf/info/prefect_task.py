from pathlib import Path

from prefect import Task

from leaf_focus.pdf.info.item import Item as PdfInfoItem
from leaf_focus.pdf.identify.item import Item as PdfIdentifyItem
from leaf_focus.pdf.info.operation import Operation


class PrefectTask(Task):
    """A Prefect task to run the pdf images operation."""

    def __init__(self, base_path: Path, exe_path: Path, **kwargs):
        super().__init__(**kwargs)
        self._operation = Operation(self.logger, base_path, exe_path)

    # noinspection PyMethodOverriding
    def run(self, input_item: PdfIdentifyItem) -> PdfInfoItem:
        """Run the task."""

        pdf_path = input_item.pdf_file
        info_path = self._operation.run(pdf_path, input_item.file_hash)
        output_item = PdfInfoItem.load_json(info_path)
        return output_item
