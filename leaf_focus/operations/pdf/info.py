import json
from logging import Logger
from pathlib import Path

from leaf_focus.components.store.location import Location
from leaf_focus.support.config import Config
from leaf_focus.components.pdf.info import Info as PdfInfo


class Info:
    def __init__(self, logger: Logger, config: Config):
        self._logger = logger
        self._config = config

        self._location = Location(logger)
        self._base_dir = config.pdf_base_dir
        self._pdf_info = PdfInfo(logger, config.exe_pdf_info_file)

    def run(self, pdf_identify_file: Path):
        """Create the pdf info file."""

        # read the identify file
        with open(pdf_identify_file, "rt") as f:
            identify = json.load(f)

        # create the pdf info file
        input_file = Path(identify.get("pdf_file"))
        file_hash = identify.get("file_hash")
        output_file = self._location.pdf_info_file(self._base_dir, file_hash)
        self._location.create_directory(output_file.parent)

        self._pdf_info.create(input_file, output_file)

        return output_file
