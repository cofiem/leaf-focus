import logging
import subprocess
from pathlib import Path


class Images:

    _logger = logging.getLogger(__name__)

    def __init__(self, exe_file: Path):
        if not exe_file:
            raise ValueError("Must supply exe file.")
        if not exe_file.exists():
            raise FileNotFoundError(f"Exe file does not exist '{exe_file}'.")
        self._exe_file = exe_file

    def create(self, pdf_file: Path, output_dir: Path, prefix: str) -> None:
        if not pdf_file:
            raise ValueError("Must supply pdf file.")
        if not output_dir:
            raise ValueError("Must supply output dir.")
        if not prefix:
            raise ValueError("Must supply prefix.")
        if not pdf_file.exists():
            raise FileNotFoundError(f"Pdf file does not exist '{pdf_file}'.")

        if not output_dir.exists():
            output_dir.mkdir(exist_ok=True, parents=True)

        commands = [
            str(self._exe_file),
            "-gray",
            str(pdf_file),
            str(output_dir / prefix),
        ]

        self._logger.info(f"Creating pdf page images for '{pdf_file}'.")

        result = subprocess.run(commands, capture_output=True, check=True)

        if result.returncode != 0:
            self._logger.error(f"Could not create pdf page images: {repr(result)}")
            raise ValueError(result)
