from logging import Logger
from pathlib import Path

from leaf_focus.ocr.recognise.component import Component
from leaf_focus.support.location import Location


class Operation:
    """A pipeline building block that creates the ocr recognise files."""

    def __init__(self, logger: Logger, base_path: Path):
        self._logger = logger
        self._base_path = base_path
        self._location = Location(logger)
        self._component = Component(logger)

    def run(self, file_hash: str, page: int, threshold: int):
        """Run the operation."""

        # crate output directory
        loc = self._location
        bd = self._base_path
        input_file = loc.pdf_page_prepared_file(bd, file_hash, page, threshold)
        annotation_file = loc.pdf_page_ocr_file(bd, file_hash, page, threshold)
        predictions_file = loc.pdf_page_text_file(bd, file_hash, page, threshold)

        # create annotation file and predictions file
        self._component.recognise_text(input_file, annotation_file, predictions_file)

        # result
        return annotation_file, predictions_file
