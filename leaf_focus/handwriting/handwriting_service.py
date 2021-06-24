import logging
from pathlib import Path


class HandwritingService:
    """Recognise handwriting."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def start(self, items_path: Path, cache_dir: Path):
        # TODO
        pass
