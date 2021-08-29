from logging import Logger
import subprocess
from pathlib import Path


class Text:
    def __init__(self, logger: Logger, exe_file: Path):
        self._logger = logger
        if not exe_file:
            raise ValueError("Must supply exe file.")
        if not exe_file.exists():
            raise FileNotFoundError(f"Exe file does not exist '{exe_file}'.")
        self._exe_file = exe_file

    def create(self, pdf_path: Path, text_path: Path) -> None:
        if not pdf_path:
            raise ValueError("Must supply pdf file.")
        if not text_path:
            raise ValueError("Must supply text file.")
        if not pdf_path.exists():
            raise FileNotFoundError(f"Pdf file does not exist '{pdf_path}'.")

        if text_path.exists():
            self._logger.debug(f"Pdf text file already exists for '{pdf_path}'.")
            return

        if not text_path.parent.exists():
            text_path.parent.mkdir(exist_ok=True, parents=True)

        commands = [
            str(self._exe_file),
            "-layout",
            "-enc",
            "UTF-8",
            "-eol",
            "dos",
            str(pdf_path),
            str(text_path),
        ]

        self._logger.info(f"Creating pdf text for '{pdf_path}'.")

        result = subprocess.run(commands, capture_output=True, check=True)

        if result.returncode != 0:
            self._logger.error(f"Could not create pdf text: {repr(result)}")
            raise ValueError(result)
