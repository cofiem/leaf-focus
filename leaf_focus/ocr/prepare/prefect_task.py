from pathlib import Path

from prefect import Task

from leaf_focus.ocr.prepare.operation import Operation


class OcrPrepareTask(Task):
    """A Prefect task to run the ocr prepare operation."""

    def __init__(self, base_path: Path, **kwargs):
        kwargs = {**kwargs, "name": "ocr.prepare"}
        super().__init__(**kwargs)
        self._operation = Operation(self.logger, base_path)

    # noinspection PyMethodOverriding
    def run(self, input_item: tuple[str, int], threshold: int) -> tuple[str, int]:
        """Run the task."""
        file_hash, page = input_item
        self._operation.run(file_hash, page, threshold)
        return file_hash, page
