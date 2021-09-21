from logging import Logger
from pathlib import Path

from leaf_focus.ocr.prepare.component import Component
from leaf_focus.support.location import Location


class Operation:
    def __init__(self, logger: Logger, base_path: Path):
        self._logger = logger
        self._base_path = base_path
        self._location = Location(logger)
        self._component = Component(logger)

    def run(self, file_hash: str, page: int, threshold: int):

        # create output directory
        loc = self._location
        bd = self._base_path
        input_file = loc.pdf_page_image_file(bd, file_hash, page)
        output_file = loc.pdf_page_prepared_file(bd, file_hash, page, threshold)
        loc.create_directory(output_file.parent)

        # create the image file
        self._component.threshold(input_file, output_file, threshold)

        # result
        return output_file
