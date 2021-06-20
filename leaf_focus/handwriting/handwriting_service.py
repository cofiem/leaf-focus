import logging
from pathlib import Path


class HandwritingService:
    """Recognise handwriting."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def start(self, input_image_path: Path):
        self._logger.info(f"Running handwriting recognition.")

        # TODO
