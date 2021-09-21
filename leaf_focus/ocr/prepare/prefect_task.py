from pathlib import Path

from prefect import Task

from leaf_focus.ocr.prepare.operation import Operation


class PrefectTask(Task):
    """A Prefect task to run the ocr prepare operation."""

    def __init__(self, base_path: Path, **kwargs):
        super().__init__(**kwargs)
        self._operation = Operation(self.logger, base_path)

    # noinspection PyMethodOverriding
    def run(self, input_item: tuple[str, int], threshold: int) -> tuple[str, int]:
        """Run the task."""
        file_hash, page = input_item
        image_path = self._operation.run(file_hash, page, threshold)
        return image_path
