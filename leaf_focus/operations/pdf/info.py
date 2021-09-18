from logging import Logger
from pathlib import Path

from leaf_focus.components.pdf.info import Info as PdfInfo
from leaf_focus.components.location import Location
from leaf_focus.support.config import Config


class Info:
    def __init__(self, logger: Logger, config: Config):
        self._logger = logger
        self._config = config

        self._location = Location(logger)
        self._base_dir = config.pdf_data_dir
        self._pdf_info = PdfInfo(logger, config.exe_pdf_info_file)

    def run(self, pdf_path: Path, file_hash: str, name: str):
        """Create the pdf info file."""
        # create the output directory
        output_file = self._location.pdf_info_file(self._base_dir, file_hash)
        self._location.create_directory(output_file.parent)

        # create the pdf info file
        self._pdf_info.create(pdf_path, output_file)

        # log completion
        self._logger.info(f"Completed pdf info for '{name}'.")
        return output_file
