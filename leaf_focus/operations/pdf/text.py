import json
from logging import Logger
from pathlib import Path

from leaf_focus.components.store.location import Location
from leaf_focus.support.config import Config
from leaf_focus.components.pdf.text import Text as PdfText


class Text:
    def __init__(self, logger: Logger, config: Config):
        self._logger = logger
        self._config = config

        self._location = Location(logger)
        self._base_dir = config.pdf_base_dir
        self._pdf_text = PdfText(logger, config.exe_pdf_text_file)

    def run(self, pdf_identify_file: Path):
        """Create the pdf text file."""

        # read the identify file
        with open(pdf_identify_file, "rt") as f:
            identify = json.load(f)

        # create the pdf text file
        input_file = Path(identify.get("pdf_file"))
        file_hash = identify.get("file_hash")
        output_file = self._location.pdf_text_file(self._base_dir, file_hash)
        self._location.create_directory(output_file.parent)

        self._pdf_text.create(input_file, output_file)

        return output_file
