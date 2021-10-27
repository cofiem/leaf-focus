import re
import subprocess
from logging import Logger
from pathlib import Path
from typing import Iterable


class Component:
    """Create pdf images."""

    def __init__(self, logger: Logger, exe_file: Path):
        self._logger = logger
        if not exe_file:
            raise ValueError("Must supply exe file.")
        if not exe_file.exists():
            raise FileNotFoundError(f"Exe file does not exist '{exe_file}'.")
        self._exe_file = exe_file

    def create(self, pdf_path: Path, output_prefix_path: Path) -> list[Path]:
        """Create images of each page of a pdf."""

        if not pdf_path:
            raise ValueError("Must supply pdf file.")
        if not output_prefix_path:
            raise ValueError("Must supply output prefix.")
        if not pdf_path.exists():
            raise FileNotFoundError(f"Pdf file does not exist '{pdf_path}'.")

        if not output_prefix_path.parent.exists():
            output_prefix_path.parent.mkdir(exist_ok=True, parents=True)

        # find the highest page number
        existing_files = sorted(
            self.read(output_prefix_path),
            key=lambda x: x[0],
        )
        page_start = None
        if len(existing_files) > 0:
            # start from the last page number
            # this ensures the last page number is overwritten
            # if it was only partially created
            last = existing_files[-1]
            page_start = last[0]

        if page_start:
            last_page_number = ["-f", str(page_start)]
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

        if page_start:
            msg_page = f" starting from page {page_start}"
        else:
            msg_page = ""

        if pdf_path:
            msg_path = pdf_path.parts[-2]
        else:
            msg_path = ""
        self._logger.info(
            f"Creating pdf page images for cache id '{msg_path}'{msg_page}."
        )

        result = subprocess.run(commands, capture_output=True, check=True)

        if result.returncode != 0:
            self._logger.error(f"Could not create pdf page images: {repr(result)}")
            raise ValueError(result)

        existing_files = sorted(
            self.read(output_prefix_path),
            key=lambda x: x[0],
        )
        return [i[1] for i in existing_files]

    def read(self, output_prefix_path: Path) -> Iterable[tuple[int, Path]]:
        pattern = re.compile(r".*-(?P<page>\d{6})$")
        for path in output_prefix_path.parent.glob("*.png"):
            if not path.is_file():
                continue

            match = pattern.search(path.stem)
            if not match:
                continue

            page = int(match.group("page"))
            yield page, path
