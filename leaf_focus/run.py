import logging
from argparse import ArgumentParser, Namespace
from pathlib import Path

from leaf_focus.download.download_service import DownloadService
from leaf_focus.download.extract.extract_service import ExtractService
from leaf_focus.handwriting.handwriting_service import HandwritingService
from leaf_focus.ocr.ocr_service import OcrService
from leaf_focus.report.report_service import ReportService


class Run:

    _activity_download = "download"
    _activity_extract = "extract"
    _activity_ocr = "ocr"
    _activity_handwriting = "handwriting"
    _activity_report = "report"

    def __init__(self):
        self._logger = None

    def from_args(self, args: Namespace):
        name = args.sub_parser_name

        if name != "download":
            self._create_logger()

        if name == self._activity_download:
            self.download(args.items_dir, args.cache_dir)
        elif name == self._activity_extract:
            self.extract(
                args.items_dir,
                args.cache_dir,
                args.pdf_to_info_file,
                args.pdf_to_text_file,
                args.pdf_to_image_file,
            )
        elif name == self._activity_ocr:
            self.ocr(args.items_dir, args.cache_dir)
        elif name == self._activity_handwriting:
            self.handwriting(args.items_dir, args.cache_dir)
        elif name == self._activity_report:
            self.report(args.items_dir, args.cache_dir, args.output_dir)
        else:
            raise ValueError(f"Unrecognised activity '{name}'.")

    def download(self, items_dir: Path, cache_dir: Path):
        dl = DownloadService()
        dl.start(items_dir, cache_dir)

    def extract(
        self,
        items_dir: Path,
        cache_dir: Path,
        pdf_info_file: Path,
        pdf_text_file: Path,
        pdf_image_file: Path,
    ):
        self._log_start(self._activity_extract)
        extract = ExtractService(
            self._logger, pdf_info_file, pdf_text_file, pdf_image_file
        )
        # TODO: integrate extract into download,
        #  only run if response is not cached or files do not exist
        extract.start(items_dir, cache_dir)
        self._log_end(self._activity_extract)

    def ocr(self, items_dir: Path, cache_dir: Path):
        self._log_start(self._activity_ocr)
        ocr = OcrService(self._logger)
        ocr.start(items_dir, cache_dir)
        self._log_end(self._activity_ocr)

    def handwriting(self, items_dir: Path, cache_dir: Path):
        self._log_start(self._activity_handwriting)
        hw = HandwritingService(self._logger)
        hw.start(items_dir, cache_dir)
        self._log_end(self._activity_handwriting)

    def report(self, items_dir: Path, cache_dir: Path, output_dir: Path):
        self._log_start(self._activity_report)
        report = ReportService(self._logger)
        report.start(items_dir, cache_dir, output_dir)
        self._log_end(self._activity_report)

    def _create_logger(self):
        logging.basicConfig(
            format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s",
            level=logging.INFO,
        )
        self._logger = logging.getLogger("leaf-focus")

    def _log_start(self, name: str):
        if self._logger:
            self._logger.info(f"Starting {name}.")

    def _log_end(self, name: str):
        if self._logger:
            self._logger.info(f"Finished {name}.")


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Extract text from pdf files.",
    )
    parser.add_argument(
        "--items-dir",
        type=Path,
        help="Path to items directory.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        help="Path to cache directory.",
    )
    subparsers = parser.add_subparsers(
        dest="sub_parser_name",
        help="Available commands.",
    )

    # create the parser for the "download" command
    sub_parser_download = subparsers.add_parser(
        "download",
        help="Download pdfs and create images and extract text from them.",
    )

    # create the parser for the "extract" command
    sub_parser_extract = subparsers.add_parser(
        "extract",
        help="Extract info, text, and images from pdfs.",
    )
    sub_parser_extract.add_argument(
        "--pdf-to-info-file",
        type=Path,
        help="Path to xpdf pdfinfo.",
    )
    sub_parser_extract.add_argument(
        "--pdf-to-text-file",
        type=Path,
        help="Path to xpdf pdftotext.",
    )
    sub_parser_extract.add_argument(
        "--pdf-to-image-file",
        type=Path,
        help="Path to xpdf pdftopng.",
    )

    # create the parser for the "ocr" command
    sub_parser_ocr = subparsers.add_parser(
        "ocr",
        help="Recognise text from each line of each pdf page.",
    )

    # create the parser for the "handwriting" command
    sub_parser_handwriting = subparsers.add_parser(
        "handwriting",
        help="Recognise text from each line of each pdf page.",
    )

    # create the parser for the "report" command
    sub_parser_report = subparsers.add_parser(
        "report",
        help="Recognise text from each line of each pdf page.",
    )
    sub_parser_report.add_argument(
        "--output-dir",
        type=Path,
        help="Path to directory to save the report files.",
    )

    parsed_args = parser.parse_args()
    if parsed_args.sub_parser_name:
        Run().from_args(parsed_args)
    else:
        parser.print_help()
