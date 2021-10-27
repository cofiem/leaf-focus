from pathlib import Path

from prefect import Task

from leaf_focus.ocr.recognise.ocr_wrapper import OcrWrapper
from leaf_focus.ocr.recognise.operation import Operation


class OcrRecogniseTask(Task):
    """A Prefect task to run the ocr recognise operation."""

    def __init__(self, base_path: Path, **kwargs):
        kwargs = {**kwargs, "name": "ocr.recognise"}
        super().__init__(**kwargs)
        self._operation = Operation(self.logger, base_path)

    # noinspection PyMethodOverriding
    def run(
        self, input_item: tuple[str, int], threshold: int, ocr_wrapper: OcrWrapper
    ) -> tuple[Path, Path]:
        """Run the task."""
        file_hash, page = input_item
        annotation_path, predictions_path = self._operation.run(
            file_hash, page, threshold, ocr_wrapper
        )
        return annotation_path, predictions_path
