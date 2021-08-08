import re
from logging import Logger
import subprocess
from pathlib import Path
from typing import List, Tuple


class Images:
    def __init__(self, exe_file: Path, logger: Logger):
        self._logger = logger
        if not exe_file:
            raise ValueError("Must supply exe file.")
        if not exe_file.exists():
            raise FileNotFoundError(f"Exe file does not exist '{exe_file}'.")
        self._exe_file = exe_file

    def create(self, pdf_file: Path, output_prefix: Path) -> List[Tuple[Path, int]]:
        if not pdf_file:
            raise ValueError("Must supply pdf file.")
        if not output_prefix:
            raise ValueError("Must supply output prefix.")
        if not pdf_file.exists():
            raise FileNotFoundError(f"Pdf file does not exist '{pdf_file}'.")

        if not output_prefix.parent.exists():
            output_prefix.parent.mkdir(exist_ok=True, parents=True)

        # find the highest page number
        existing_files = self._find_images(output_prefix)
        last_page_number = (
            ["-f", str(existing_files[-1][1])] if len(existing_files) > 0 else []
        )

        # −f : Specifies the first page to convert.
        # -r : Specifies the resolution, in DPI. The default is 150 DPI.
        commands = (
            [
                str(self._exe_file),
                "-gray",
                "-r",
                "150",
            ]
            + last_page_number
            + [
                str(pdf_file),
                str(output_prefix),
            ]
        )

        self._logger.info(f"Creating pdf page images for '{pdf_file}'.")

        result = subprocess.run(commands, capture_output=True, check=True)

        if result.returncode != 0:
            self._logger.error(f"Could not create pdf page images: {repr(result)}")
            raise ValueError(result)

        existing_files = self._find_images(output_prefix)
        return existing_files

    def _find_images(self, output_prefix: Path):
        found = []
        file_pattern = re.compile(rf"^{output_prefix.name}-(\d{{6}})$")
        for file in output_prefix.parent.glob(output_prefix.name + "*.png"):
            if not file.is_file():
                continue
            match = file_pattern.match(file.name)
            if match:
                found.append((file, int(match.group(1), 10)))
        found = sorted(found, key=lambda x: x[1])
        return found
