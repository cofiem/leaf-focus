import subprocess
from logging import Logger
from pathlib import Path

from leaf_focus.download.items.pdf_item import PdfItem


class ExtractService:

    _item_prefix = "items"
    _item_suffix = ".csv"

    def __init__(
        self,
        logger: Logger,
        pdf_info_path: Path,
        pdf_text_path: Path,
        pdf_image_path: Path,
    ):
        self._logger = logger
        self._pdf_info_path = pdf_info_path
        self._pdf_text_path = pdf_text_path
        self._pdf_image_path = pdf_image_path

    def start(self, items_dir: Path, cache_dir: Path):
        if not items_dir.exists() or not items_dir.is_dir():
            self._logger.error(f"Could not find items dir '{items_dir}'.")
            return

        self._logger.info(
            f"Running pdf data extraction using item csv files in '{items_dir}'."
        )

        pattern = f"{self._item_prefix}*{self._item_suffix}"
        for item_file in items_dir.glob(pattern):
            for item in PdfItem.load(item_file):
                item_path = Path(item["path"])
                self._logger.info(f"Processing '{item_path}'.")

                info_file = item_path.parent / "response_body_info"
                self.create_info(item_path, info_file)

                text_file = item_path.parent / "response_body_text"
                self.create_text(item_path, text_file)

                image_prefix = item_path.parent / "response_body_image"
                self.create_images(item_path, image_prefix)

    def create_info(self, input_path: Path, output_path: Path):
        if not input_path or not input_path.exists():
            self._logger.error(f"Could not find pdf file '{input_path}'.")

        commands = [str(self._pdf_info_path), str(input_path)]
        result = subprocess.run(commands, capture_output=True, check=True)
        is_success = result.returncode == 0
        if is_success:
            output_path.write_text(data=result.stdout.decode("utf8"), encoding="utf8")
        else:
            self._logger.error(f"Pdf to info command failed: {repr(result)}")
        return is_success

    def create_text(self, input_path: Path, output_path: Path):
        if not input_path or not input_path.exists():
            self._logger.error(f"Could not find pdf file '{input_path}'.")

        # if not text_file.exists():
        commands = [
            str(self._pdf_text_path),
            "-layout",
            "-enc",
            "UTF-8",
            "-eol",
            "dos",
            str(input_path),
            str(output_path),
        ]
        result = subprocess.run(commands, capture_output=True, check=True)
        is_success = result.returncode == 0
        if not is_success:
            self._logger.error(f"Pdf to text command failed: {repr(result)}")
        return is_success

    def create_images(self, input_path: Path, output_prefix_path: Path):
        if not input_path or not input_path.exists():
            self._logger.error(f"Could not find pdf file '{input_path}'.")

        commands = [
            str(self._pdf_image_path),
            "-gray",
            str(input_path),
            str(output_prefix_path),
        ]
        result = subprocess.run(commands, capture_output=True, check=True)
        is_success = result.returncode == 0
        if not is_success:
            self._logger.error(f"Pdf to image command failed: {repr(result)}")
        return is_success
