from logging import Logger
from pathlib import Path

from leaf_focus.support.location import Location
from leaf_focus.pdf.info.component import Component


class Operation:
    """A pipeline building block that creates the pdf info file."""

    def __init__(self, logger: Logger, base_path: Path, exe_path: Path):
        self._logger = logger
        self._base_path = base_path
        self._location = Location(logger)
        self._component = Component(logger, exe_path)

    def run(self, pdf_path: Path, file_hash: str):
        """Run the operation."""

        # create the output directory
        output_file = self._location.info_file(self._base_path, file_hash)
        self._location.create_directory(output_file.parent)

        # create the pdf info file
        self._component.create(pdf_path, output_file)

        # result
        return output_file
