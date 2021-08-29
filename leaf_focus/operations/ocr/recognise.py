from logging import Logger

from leaf_focus.components.ocr.recognise import Recognise as OcrRecognise
from leaf_focus.components.location import Location
from leaf_focus.support.config import Config


class Recognise:
    def __init__(self, config: Config, logger: Logger):
        self._logger = logger
        self._config = config

        self._location = Location(logger)
        self._base_dir = config.pdf_base_dir
        self._recognise = OcrRecognise(logger)

    def run(self, file_hash: str, name: str, page: int, threshold: int):
        """ "Run image OCR and save the output."""
        # crate output directory
        loc = self._location
        bd = self._base_dir
        input_file = loc.pdf_page_prepared_file(bd, file_hash, page, threshold)
        annotation_file = loc.pdf_page_ocr_file(bd, file_hash, page, threshold)
        predictions_file = loc.pdf_page_text_file(bd, file_hash, page, threshold)

        # create annotation file and predictions file
        self._recognise.recognise_text(input_file, annotation_file, predictions_file)

        # log completion
        self._logger.info(f"Completed ocr recognise for '{name}'.")
        return annotation_file, predictions_file
