import json
from logging import Logger
from pathlib import Path

from leaf_focus.components.store.location import Location
from leaf_focus.support.config import Config
from leaf_focus.components.pdf.images import Images as PdfImages


class Images:
    def __init__(self, logger: Logger, config: Config):
        self._logger = logger
        self._config = config

        self._location = Location(logger)
        self._base_dir = config.pdf_base_dir
        self._pdf_images = PdfImages(logger, config.exe_pdf_images_file)

    def run(self, pdf_identify_file: Path):
        """Create the pdf image files."""

        # read the identify file
        with open(pdf_identify_file, "rt") as f:
            identify = json.load(f)

        # create the pdf page images
        input_file = Path(identify.get("pdf_file"))
        file_hash = identify.get("file_hash")
        output_prefix = self._location.pdf_images_path(self._base_dir, file_hash)
        self._location.create_directory(output_prefix.parent)
        pdf_image_files = self._pdf_images.create(input_file, output_prefix)

        return pdf_image_files
