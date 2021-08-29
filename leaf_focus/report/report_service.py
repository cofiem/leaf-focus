import csv
import dataclasses
import logging
from pathlib import Path

from leaf_focus.components.data.pdf_item import PdfItem
from leaf_focus.report.content_item import ContentItem
from leaf_focus.report.content_report import ContentReport
from leaf_focus.report.metadata_item import MetadataItem
from leaf_focus.report.metadata_report import MetadataReport


class ReportService:
    """Create a csv report from the pdf files."""

    _item_prefix = "items"
    _csv_suffix = ".csv"

    _text_name = "response_body_text"
    _info_name = "response_body_info"

    _ocr_prefix = "response_body_image"
    _ocr_id = "found-text"

    _file_metadata = "metadata.csv"
    _file_content = "content.csv"

    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._metadata_report = MetadataReport(self._logger)
        self._content_report = ContentReport(self._logger)

    def start(self, items_dir: Path, cache_dir: Path, output_dir: Path) -> None:
        if not items_dir.exists() or not items_dir.is_dir():
            self._logger.error(f"Could not find items dir '{items_dir}'.")
            return

        self._logger.info(f"Parsing text from item csv files in '{items_dir}'.")

        pattern = f"{self._item_prefix}*{self._csv_suffix}"

        matched_item_files = sorted(
            items_dir.glob(pattern), key=lambda x: x.name, reverse=True
        )

        # write reports
        metadata_path = output_dir / self._file_metadata
        metadata_open = open(metadata_path, "wt", newline="", encoding="utf8")

        content_path = output_dir / self._file_content
        content_open = open(content_path, "wt", newline="", encoding="utf8")

        with metadata_open as metadata_f, content_open as content_f:
            metadata_fields = [i.name for i in dataclasses.fields(MetadataItem)]
            metadata_writer = csv.DictWriter(metadata_f, metadata_fields)
            metadata_writer.writeheader()

            content_fields = [i.name for i in dataclasses.fields(ContentItem)]
            content_writer = csv.DictWriter(content_f, content_fields)
            content_writer.writeheader()

            for item_file in matched_item_files:
                for metadata_item, content_items in self.process_item(item_file):
                    metadata_writer.writerow(dataclasses.asdict(metadata_item))

                    for content_item in content_items:
                        content_writer.writerow(dataclasses.asdict(content_item))

    def process_item(self, item_file: Path):
        if not item_file.exists() or not item_file.is_file():
            self._logger.error(f"Could not find item file '{item_file}'.")
            return

        # TODO: only process the most recent files at first
        referrers = [
            "https://www.aph.gov.au/Senators_and_Members/Members/Register",
            "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Senators_Interests/Register46thparl",
        ]

        for item in PdfItem.load(item_file):
            item_path = Path(item["path"])

            if not item_path.exists():
                self._logger.error(f"Could not find item path '{item_path}'.")
                continue

            referrer = item["referrer"]
            if referrer not in referrers:
                continue

            parent_dir = item_path.parent

            text_file = parent_dir / self._text_name
            info_file = parent_dir / self._info_name
            csv_files = []

            # find the ocr csv files
            pattern = f"{self._ocr_prefix}*{self._ocr_id}*{self._csv_suffix}"
            for csv_file in parent_dir.glob(pattern):
                csv_files.append(csv_file)

            text_info = self.read_info(info_file)
            text_extracted = self.read_text(text_file)
            text_found = [list(PdfItem.load(p)) for p in csv_files]

            metadata_item = self._metadata_report.start(item, text_info)
            content_items = self._content_report.start(
                metadata_item, text_extracted, text_found
            )

            yield metadata_item, content_items

    def read_info(self, path: Path):
        result = {}
        if not path.exists():
            return result
        unknown_count = 1
        with open(path, "rt", encoding="utf8") as f:
            for line in f.readlines():
                if not line or not line.strip():
                    continue
                if ":" in line:
                    key, value = line.split(":", maxsplit=1)
                else:
                    key = f"unknown{unknown_count}"
                    value = line
                    unknown_count += 1
                result[key.strip()] = value.strip()
        return result

    def read_text(self, path: Path):
        result = []
        with open(path, "rt", encoding="utf8") as f:
            # read the whole file
            content = f.read() or ""

            # replace Carriage Return with New Line
            # split on Form Feed (which xpdf pdftotext uses to indicate end of page)
            # ignore the last item of array as that's after the last Form Feed
            pages = content.replace("\r", "\n").split("\f")[:-1]

            for page in pages:

                # read each line in each page
                page_lines = []
                for line in page.split("\n"):
                    page_lines.append(line)

                # add the page if there are any lines
                if len(page_lines) > 0:
                    result.append(page_lines)
        return result
