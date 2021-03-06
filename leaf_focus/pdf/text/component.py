import subprocess
from logging import Logger
from pathlib import Path


class Component:
    """Creates the pdf text file."""

    def __init__(self, logger: Logger, exe_file: Path):
        self._logger = logger
        if not exe_file:
            raise ValueError("Must supply exe file.")
        if not exe_file.exists():
            raise FileNotFoundError(f"Exe file does not exist '{exe_file}'.")
        self._exe_file = exe_file

    def create(self, pdf_path: Path, text_path: Path) -> None:
        """Extract the text from a pdf to a text file."""

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

        # uses -table instead of -layout because there are a few tables
        # the -table setting preserves the table structure better than -layout
        commands = [
            str(self._exe_file),
            "-table",
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

    @classmethod
    def read(cls, path: Path):
        result = []
        with open(path, "rt", encoding="utf-8") as f:
            # read the whole file
            content = f.read() or ""

        # Carriage Return (CR) character (0x0D, \r)
        # Line Feed (LF) character (0x0A, \n)
        # End of Line (EOL) sequence (0x0D 0x0A, \r\n)
        # Double Line Feed (\n\n)
        # replace with LF
        find = ["\n\n", "\r\n", "\r"]
        replacement = "\n"
        pages = content
        for item in find:
            pages = pages.replace(item, replacement)

        # split on Form Feed (\f) (pdftotext uses to indicate end of page)
        pages = pages.split("\f")

        # if the last item of array is empty ignore it,
        # as that's after the last Form Feed
        if not pages[-1]:
            pages = pages[:-1]

        for page in pages:
            # read each line in each page
            page_lines = []
            for line in (page or "").split(replacement):
                if line:
                    page_lines.append(line)

            # add the page even if there are no lines
            result.append(page_lines)

        return result
