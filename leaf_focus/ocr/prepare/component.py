from logging import Logger
from pathlib import Path
from PIL import Image


class Component:
    """Create the image file ready for OCR."""

    def __init__(self, logger: Logger):
        self._logger = logger

    def threshold(self, input_file: Path, output_file: Path, threshold: int) -> None:
        """Create the threshold image file."""

        if not input_file:
            raise ValueError("Must supply input file.")
        if not output_file:
            raise ValueError("Must supply output file.")
        if not input_file.exists():
            raise FileNotFoundError(f"Input file does not exist '{input_file}'.")
        if threshold < 0 or threshold > 255:
            raise ValueError(f"Threshold must between 0 and 255, not {threshold}.")

        if output_file.exists():
            self._logger.debug(f"Prepared image already exists for '{input_file}'.")
            return

        self._logger.info(f"Creating threshold image for '{input_file}'.")

        img = Image.open(input_file)

        def calc_threshold(value):
            return 255 if value > threshold else 0

        img_greyscale = img.convert("L")  # type: Image
        img_threshold = img_greyscale.point(calc_threshold, mode="1")  # type: Image
        img_threshold.save(output_file)
