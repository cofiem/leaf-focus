from logging import Logger
import subprocess
from pathlib import Path


class Info:
    def __init__(self, logger: Logger, exe_file: Path):
        self._logger = logger
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
            self._logger.debug(f"Pdf info file already exists for '{pdf_file}'.")
            return

        if not info_file.parent.exists():
            info_file.parent.mkdir(exist_ok=True, parents=True)

        commands = [str(self._exe_file), str(pdf_file)]
        result = subprocess.run(commands, capture_output=True, check=True)

        if result.returncode != 0:
            self._logger.error(f"Could not create pdf info: {repr(result)}")
            raise ValueError(result)

        data = result.stdout.decode(encoding="utf8", errors="replace")
        info_file.write_text(data=data, encoding="utf8")
