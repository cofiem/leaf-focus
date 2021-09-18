from logging import Logger
from pathlib import Path

from leaf_focus.components.pdf.images import Images as PdfImages
from leaf_focus.components.location import Location
from leaf_focus.support.config import Config


class Images:
    def __init__(self, logger: Logger, config: Config):
        self._logger = logger
        self._config = config

        self._location = Location(logger)
        self._base_dir = config.pdf_data_dir
        self._pdf_images = PdfImages(logger, config.exe_pdf_images_file)

    def run(self, pdf_path: Path, file_hash: str, name: str):
        """Create the pdf image files."""
        # create the output directory
        output_prefix = self._location.pdf_images_path(self._base_dir, file_hash)
        self._location.create_directory(output_prefix.parent)

        # create the pdf page images
        pdf_image_paths = self._pdf_images.create(pdf_path, output_prefix)

        # log completion
        self._logger.info(f"Completed pdf images for '{name}'.")
        return pdf_image_paths
