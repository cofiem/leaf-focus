import json
from logging import Logger
from pathlib import Path

from leaf_focus.components.store.location import Location
from leaf_focus.support.config import Config
from leaf_focus.components.ocr.recognise import Recognise as OcrRecognise


class Recognise:
    def __init__(self, config: Config, logger: Logger):
        self._logger = logger
        self._config = config

        self._location = Location(logger)
        self._base_dir = config.pdf_base_dir
        self._recognise = OcrRecognise(logger)

    def run(self, pdf_identify_file: Path, page: int, threshold: int):
        """ "Run image OCR and save the output."""

        # read the identify file
        with open(pdf_identify_file, "rt") as f:
            identify = json.load(f)

        # create the image file
        loc = self._location
        bd = self._base_dir
        file_hash = identify.get("file_hash")
        input_file = loc.pdf_page_prepared_file(bd, file_hash, page, threshold)
        annotation_file = loc.pdf_page_ocr_file(bd, file_hash, page, threshold)
        predictions_file = loc.pdf_page_text_file(bd, file_hash, page, threshold)

        pdf_details_path = loc.details_file(input_file)
        with open(pdf_details_path, "rt") as f:
            details = json.load(f)

        self._logger.info(f"Started ocr recognise for '{details.get('name')}'.")

        self._recognise.recognise_text(input_file, annotation_file, predictions_file)

        self._logger.info(f"Completed ocr recognise for '{details.get('name')}'.")
        return annotation_file, predictions_file
