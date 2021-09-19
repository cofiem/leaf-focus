from logging import Logger
from pathlib import Path


from leaf_focus.support.location import Location
from leaf_focus.pdf.identify.component import Component


class Operation:
    """A pipeline building block that creates the pdf identify file."""

    def __init__(self, logger: Logger, base_path: Path):
        self._logger = logger
        self._base_path = base_path
        self._location = Location(logger)
        self._component = Component(logger)

    def run(self, pdf_path: Path):
        """Run the operation."""

        self._logger.info(f"Creating pdf identify for '{pdf_path}'.")

        # generate file hash
        file_hash = self._component.file_hash(pdf_path)

        # create the output directory
        output_file = self._location.identify_file(self._base_path, file_hash)
        self._location.create_directory(output_file.parent)

        # create output file
        self._component.create(pdf_path, file_hash, output_file)

        # result
        return output_file
