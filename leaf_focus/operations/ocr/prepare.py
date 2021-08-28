import json
from logging import Logger
from pathlib import Path

from leaf_focus.components.store.location import Location
from leaf_focus.support.config import Config
from leaf_focus.components.ocr.prepare import Prepare as OcrPrepare


class Prepare:
    def __init__(self, logger: Logger, config: Config):
        self._logger = logger
        self._config = config

        self._location = Location(logger)
        self._base_dir = config.pdf_base_dir
        self._prepare = OcrPrepare(logger, config.exe_pdf_text_file)

    def run(self, pdf_identify_file: Path, page: int, threshold: int):
        """Create the image file ready for OCR."""

        # read the identify file
        with open(pdf_identify_file, "rt") as f:
            identify = json.load(f)

        # create the image file
        loc = self._location
        bd = self._base_dir
        file_hash = identify.get("file_hash")
        input_file = loc.pdf_page_image_file(bd, file_hash, page)
        output_file = loc.pdf_page_prepared_file(bd, file_hash, page, threshold)

        pdf_details_path = loc.details_file(input_file)
        with open(pdf_details_path, "rt") as f:
            details = json.load(f)

        self._logger.info(f"Started ocr prepare for '{details.get('name')}'.")

        self._prepare.threshold(input_file, output_file, threshold)

        self._logger.info(f"Completed ocr prepare for '{details.get('name')}'.")
        return output_file
