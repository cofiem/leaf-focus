from logging import Logger

from leaf_focus.components.ocr.prepare import Prepare as OcrPrepare
from leaf_focus.components.location import Location
from leaf_focus.support.config import Config


class Prepare:
    def __init__(self, logger: Logger, config: Config):
        self._logger = logger
        self._config = config

        self._location = Location(logger)
        self._base_dir = config.pdf_base_dir
        self._prepare = OcrPrepare(logger, config.exe_pdf_text_file)

    def run(self, file_hash: str, name: str, page: int, threshold: int):
        """Create the image file ready for OCR."""

        # create output directory
        loc = self._location
        bd = self._base_dir
        input_file = loc.pdf_page_image_file(bd, file_hash, page)
        output_file = loc.pdf_page_prepared_file(bd, file_hash, page, threshold)
        self._location.create_directory(output_file.parent)

        # create the image file
        self._prepare.threshold(input_file, output_file, threshold)

        # log completion
        self._logger.info(f"Completed ocr prepare for '{name}'.")
        return output_file
