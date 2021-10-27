from pathlib import Path
from typing import Iterable

from prefect import Task

from leaf_focus.pdf.identify.item import Item as PdfIdentifyItem
from leaf_focus.pdf.images.operation import Operation
from leaf_focus.pdf.images.item import Item as ImageItem


class PdfImagesTask(Task):
    """A Prefect task to run the pdf images operation."""

    def __init__(self, base_path: Path, exe_path: Path, **kwargs):
        kwargs = {**kwargs, "name": "pdf.images"}
        super().__init__(**kwargs)
        self._operation = Operation(self.logger, base_path, exe_path)

    # noinspection PyMethodOverriding
    def run(self, input_item: PdfIdentifyItem) -> Iterable[tuple[str, int]]:
        """Run the task."""
        pdf_path = input_item.pdf_file
        file_hash = input_item.file_hash
        self._operation.run(pdf_path, file_hash)
        result = []
        for item in self._operation.read(file_hash):
            result.append((file_hash, item.page))
        return result


class PdfImagesLoadTask(Task):
    """A Prefect task to load the pdf images."""

    def __init__(self, base_path: Path, **kwargs):
        kwargs = {**kwargs, "name": "pdf.images.load"}
        super().__init__(**kwargs)
        self._base_path = base_path

    def run(self) -> Iterable[tuple[str, int]]:
        """Run the task."""
        result = []
        for json_path in self._base_path.rglob("pdf-identify.json"):
            pdf_identify = PdfIdentifyItem.read(json_path)
            for pdf_image in ImageItem.load(json_path.parent):
                if pdf_image.variety is not None:
                    continue
                if pdf_image.threshold is not None:
                    continue
                result.append((pdf_identify.file_hash, pdf_image.page))
            break
        return result
