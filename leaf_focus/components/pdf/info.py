import logging
import subprocess
from pathlib import Path


class Info:

    _logger = logging.getLogger(__name__)

    def __init__(self, exe_file: Path):
        if not exe_file:
            raise ValueError("Must supply exe file.")
        if not exe_file.exists():
            raise FileNotFoundError(f"Exe file does not exist '{exe_file}'.")
        self._exe_file = exe_file

    def create(self, pdf_file: Path, info_file: Path) -> None:
        if not pdf_file:
            raise ValueError("Must supply pdf file.")
        if not info_file:
            raise ValueError("Must supply info file.")
        if not pdf_file.exists():
            raise FileNotFoundError(f"Pdf file does not exist '{pdf_file}'.")
        if info_file.exists():
            raise FileExistsError(f"Info file already exists '{info_file}'.")

        if not info_file.parent.exists():
            info_file.parent.mkdir(exist_ok=True, parents=True)

        commands = [str(self._exe_file), str(pdf_file)]
        result = subprocess.run(commands, capture_output=True, check=True)

        if result.returncode != 0:
            self._logger.error(f"Could not create pdf info: {repr(result)}")
            raise ValueError(result)

        info_file.write_text(data=result.stdout.decode("utf8"), encoding="utf8")
