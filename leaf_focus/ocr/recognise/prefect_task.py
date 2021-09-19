from pathlib import Path

from prefect import Task

from ocr.recognise.operation import Operation


class PrefectTask(Task):
    """A Prefect task to run the ocr recognise operation."""

    def __init__(self, base_path: Path, **kwargs):
        super().__init__(**kwargs)
        self._operation = Operation(self.logger, base_path)

    # noinspection PyMethodOverriding
    def run(self, file_hash: str, page: int, threshold: int):
        """Run the task."""

        annotation_path, predictions_path = self._operation.run(
            file_hash, page, threshold
        )
        return {
            "annotation_path": str(annotation_path),
            "predictions_path": str(predictions_path),
        }