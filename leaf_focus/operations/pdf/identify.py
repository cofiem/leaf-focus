from logging import Logger
from pathlib import Path

from leaf_focus.components.pdf.identify import Identify as StoreIdentify
from leaf_focus.components.location import Location
from leaf_focus.support.config import Config


class Identify:
    def __init__(self, logger: Logger, config: Config):
        self._logger = logger
        self._config = config

        self._location = Location(logger)
        self._base_dir = config.pdf_base_dir
        self._identify = StoreIdentify(logger)

    def run(self, pdf_path: Path, name: str):
        """Create the pdf identify file containing file hash details."""

        # generate file hash
        file_hash = self._identify.file_hash(pdf_path)

        # create the output directory
        output_file = self._location.identify_file(self._base_dir, file_hash)
        self._location.create_directory(output_file.parent)

        # create output file
        self._identify.create(pdf_path, file_hash, output_file)

        # log completion
        self._logger.info(f"Completed pdf identify for '{name}'.")
        return output_file
