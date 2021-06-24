import logging
from pathlib import Path


class ReportService:
    """Create a csv report from the pdf files."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def start(self, items_path: Path, cache_dir: Path, output_file: Path):
        # TODO
        pass
