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

    def run(self, pdf_identify_file: Path, threshold: int, page: int):
        """ "Run image OCR and save the output."""

        # read the identify file
        with open(pdf_identify_file, "rt") as f:
            identify = json.load(f)

        # create the image file
        loc = self._location
        bd = self._base_dir
        file_hash = identify.get("file_hash")
        input_file = loc.pdf_page_image_file(bd, file_hash, page)
        annotation_file = loc.pdf_page_ocr_file(bd, file_hash, threshold, page)
        predictions_file = loc.pdf_page_text_file(bd, file_hash, threshold, page)

        self._recognise.recognise_text(input_file, annotation_file, predictions_file)

        return annotation_file, predictions_file
