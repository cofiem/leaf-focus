import logging
import os
from argparse import ArgumentParser
from pathlib import Path

from leaf_focus.download.download_service import DownloadService
from leaf_focus.handwriting.handwriting_service import HandwritingService
from leaf_focus.ocr.ocr_service import OCRService
from leaf_focus.text.found_text import FoundText
from leaf_focus.text.text_service import TextService


class Run:
    def __init__(self):
        self._logger = None

    def start(self, activity: str):
        if activity != "download":
            self._configure_logging()
        if self._logger:
            self._logger.info("Starting.")
        if activity == "download":
            if not os.getenv("CUSTOM_HTTP_CACHE_DIR"):
                raise ValueError("Must set env var 'CUSTOM_HTTP_CACHE_DIR'.")
            self.download()

        elif activity == "ocr":
            if (
                not os.getenv("CUSTOM_OCR_INPUT_IMAGE")
                or not os.getenv("CUSTOM_OCR_OUTPUT_IMAGE")
                or not os.getenv("CUSTOM_OCR_OUTPUT_CSV")
            ):
                raise ValueError(
                    "Must set env vars 'CUSTOM_OCR_INPUT_IMAGE', 'CUSTOM_OCR_OUTPUT_IMAGE', 'CUSTOM_OCR_OUTPUT_CSV'."
                )

            self.ocr(
                Path(os.getenv("CUSTOM_OCR_INPUT_IMAGE")),
                Path(os.getenv("CUSTOM_OCR_OUTPUT_IMAGE")),
                Path(os.getenv("CUSTOM_OCR_OUTPUT_CSV")),
            )

        elif activity == "text":
            if not os.getenv("CUSTOM_TEXT_INPUT_CSV"):
                raise ValueError("Must set env vars 'CUSTOM_TEXT_INPUT_CSV'")

            self.text(Path(os.getenv("CUSTOM_TEXT_INPUT_CSV")))

        elif activity == "handwriting":
            if not os.getenv("CUSTOM_HANDWRITING_INPUT_IMAGE"):
                raise ValueError("Must set env vars 'CUSTOM_TEXT_INPUT_CSV'")

            self.handwriting(Path(os.getenv("CUSTOM_HANDWRITING_INPUT_IMAGE")))

        else:
            msg = f"Unrecognised activity '{activity}'."
            self._logger.error(msg)
            raise ValueError(msg)

        if self._logger:
            self._logger.info("Finished.")

    def _configure_logging(self):
        logging.basicConfig(
            format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s",
            level=logging.INFO,
        )
        self._logger = logging.getLogger("leaf-focus")

    def download(self):
        dl = DownloadService()
        dl.start()

    def ocr(
        self,
        input_image_path: Path,
        output_image_path: Path,
        output_csv_path: Path,
    ):
        ocr = OCRService(self._logger)
        ocr.start(input_image_path, output_image_path, output_csv_path)

    def text(self, input_csv_path: Path):
        text = TextService(self._logger)
        items = list(FoundText.load(input_csv_path))
        lines = list(text.order_text_lines(items))

        a = 1

    def handwriting(self, input_image_path: Path):
        hw = HandwritingService(self._logger)
        hw.start(input_image_path)


if __name__ == "__main__":
    parser = ArgumentParser(description="Extract text from pdf files.")
    parser.add_argument(
        "activity",
        choices=["download", "ocr", "text", "handwriting"],
        help="The activity to run.",
    )
    args = parser.parse_args()
    Run().start(args.activity)
