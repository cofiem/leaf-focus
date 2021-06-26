import logging
from pathlib import Path

from leaf_focus.download.items.pdf_item import PdfItem
from leaf_focus.ocr.found_text import FoundText
from leaf_focus.report.parse_text import ParseText


class ReportService:
    """Create a csv report from the pdf files."""

    _item_prefix = "items"
    _csv_suffix = ".csv"

    _text_name = "response_body_text"
    _info_name = "response_body_info"

    _ocr_prefix = "response_body_image"
    _ocr_id = "found-text"

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def start(self, items_dir: Path, cache_dir: Path, output_file: Path):
        if not items_dir.exists() or not items_dir.is_dir():
            self._logger.error(f"Could not find items dir '{items_dir}'.")
            return

        self._logger.info(f"Parsing text from item csv files in '{items_dir}'.")

        pattern = f"{self._item_prefix}*{self._csv_suffix}"
        for item_file in items_dir.glob(pattern):
            self.process_item(item_file)

    def process_item(self, item_file: Path):
        if not item_file.exists() or not item_file.is_file():
            self._logger.error(f"Could not find item file '{item_file}'.")
            return

        for item in PdfItem.load(item_file):
            item_path = Path(item["path"])

            if not item_path.exists():
                self._logger.error(f"Could not find item path '{item_path}'.")
                return

            parent_dir = item_path.parent

            text_file = parent_dir / self._text_name
            info_file = parent_dir / self._info_name
            csv_files = []

            # find the ocr csv files
            pattern = f"{self._ocr_prefix}*{self._ocr_id}*{self._csv_suffix}"
            for csv_file in parent_dir.glob(pattern):
                csv_files.append(csv_file)

            self.evaluate_text(info_file, text_file, csv_files)

    def evaluate_text(self, info_file: Path, text_file: Path, csv_files: list[Path]):
        text_info = self.read_info(info_file)
        text_extracted = self.read_text(text_file)
        text_found = [list(FoundText.load(p)) for p in csv_files]
        parse_text = ParseText(self._logger)
        result = parse_text.start(text_info, text_extracted, text_found)
        return result

    def read_info(self, path: Path):
        result = {}
        if not path.exists():
            return result
        with open(path, "rt", encoding="utf8") as f:
            for line in f.readlines():
                if not line or not line.strip():
                    continue
                key, value = line.split(":", maxsplit=1)
                result[key.strip()] = value.strip()
        return result

    def read_text(self, path: Path):
        result = []
        with open(path, "rt", encoding="utf8") as f:
            for raw_line in f.readlines():
                line = raw_line.strip()
                result.append(line)
        return result
