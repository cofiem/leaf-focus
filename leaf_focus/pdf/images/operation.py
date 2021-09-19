from logging import Logger
from pathlib import Path

from leaf_focus.support.location import Location
from leaf_focus.pdf.images.component import Component


class Operation:
    """A pipeline building block that creates the pdf page images file."""

    def __init__(self, logger: Logger, base_path: Path, exe_path: Path):
        self._logger = logger
        self._base_path = base_path
        self._location = Location(logger)
        self._component = Component(logger, exe_path)

    def run(self, pdf_path: Path, file_hash: str):
        """Run the operation."""

        # create the output directory
        output_prefix = self._location.pdf_images_path(self._base_path, file_hash)
        self._location.create_directory(output_prefix.parent)

        # create the pdf page images
        pdf_image_paths = self._component.create(pdf_path, output_prefix)

        # result
        return pdf_image_paths
