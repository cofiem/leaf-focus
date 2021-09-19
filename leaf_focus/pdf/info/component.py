import subprocess
from logging import Logger
from pathlib import Path
from typing import Iterable

from leaf_focus.pdf.info.item import Item


class Component:
    """Creates and reads a pdf info file."""

    def __init__(self, logger: Logger, exe_file: Path):
        self._logger = logger
        if not exe_file:
            raise ValueError("Must supply exe file.")
        if not exe_file.exists():
            raise FileNotFoundError(f"Exe file does not exist '{exe_file}'.")
        self._exe_file = exe_file

    def create(self, pdf_path: Path, info_path: Path) -> None:
        """Create the pdf info file."""

        if not pdf_path:
            raise ValueError("Must supply pdf file.")
        if not info_path:
            raise ValueError("Must supply info file.")
        if not pdf_path.exists():
            raise FileNotFoundError(f"Pdf file does not exist '{pdf_path}'.")

        if info_path.exists():
            self._logger.debug(f"Pdf info file already exists for '{pdf_path}'.")
            return

        if not info_path.parent.exists():
            info_path.parent.mkdir(exist_ok=True, parents=True)

        commands = [
            str(self._exe_file),
            "-enc",
            "UTF-8",
            str(pdf_path),
        ]

        self._logger.info(f"Creating pdf info for '{pdf_path}'.")

        result = subprocess.run(commands, capture_output=True, check=True)

        if result.returncode != 0:
            self._logger.error(f"Could not create pdf info: {repr(result)}")
            raise ValueError(result)

        content = result.stdout.decode(encoding="utf8", errors="replace")
        lines = content.replace("\r\n", "\n").replace("\r", "\n").splitlines()
        entries = self._parse_output(lines)
        item = Item(pdf_path=pdf_path, entries=entries)
        item.save_json(info_path)

    def _parse_output(self, lines: Iterable[str]) -> dict[str, str]:
        result = {}
        unknown_count = 0
        for line in lines:
            if not line or not line.strip():
                continue
            if ":" in line:
                key, value = line.split(":", maxsplit=1)
            else:
                unknown_count += 1
                key = f"unknown{unknown_count}"
                value = line

            result[key.strip()] = value.strip()

        if unknown_count > 0:
            self._logger.warning(
                f"Found {unknown_count} unknown keys in pdf info file."
            )

        return result
