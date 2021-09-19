from pathlib import Path

from prefect import Task

from ocr.prepare.operation import Operation


class PrefectTask(Task):
    """A Prefect task to run the ocr prepare operation."""

    def __init__(self, base_path: Path, **kwargs):
        super().__init__(**kwargs)
        self._operation = Operation(self.logger, base_path)

    # noinspection PyMethodOverriding
    def run(self, file_hash: str, page: int, threshold: int):
        """Run the task."""

        image_path = self._operation.run(file_hash, page, threshold)
        return str(image_path)
