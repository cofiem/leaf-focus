import re
from logging import Logger
import subprocess
from pathlib import Path
from typing import List, Tuple


class Images:
    def __init__(self, logger: Logger, exe_file: Path):
        self._logger = logger
        if not exe_file:
            raise ValueError("Must supply exe file.")
        if not exe_file.exists():
            raise FileNotFoundError(f"Exe file does not exist '{exe_file}'.")
        self._exe_file = exe_file

    def create(
        self, pdf_path: Path, output_prefix_path: Path
    ) -> List[Tuple[Path, int]]:
        if not pdf_path:
            raise ValueError("Must supply pdf file.")
        if not output_prefix_path:
            raise ValueError("Must supply output prefix.")
        if not pdf_path.exists():
            raise FileNotFoundError(f"Pdf file does not exist '{pdf_path}'.")

        if not output_prefix_path.parent.exists():
            output_prefix_path.parent.mkdir(exist_ok=True, parents=True)

        # find the highest page number
        existing_files = self._find_images(output_prefix_path)
        if len(existing_files) > 0:
            # start from the last page number
            # this ensures the last page number is overwritten if it was only partially created
            last_path, last_number = existing_files[-1]
            last_page_number = ["-f", str(last_number)]
        else:
            last_page_number = []

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
                str(pdf_path),
                str(output_prefix_path),
            ]
        )

        self._logger.info(f"Creating pdf page images for '{pdf_path}'.")

        result = subprocess.run(commands, capture_output=True, check=True)

        if result.returncode != 0:
            self._logger.error(f"Could not create pdf page images: {repr(result)}")
            raise ValueError(result)

        existing_files = self._find_images(output_prefix_path)
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
