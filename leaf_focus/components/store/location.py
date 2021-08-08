from logging import Logger
from pathlib import Path


class Location:

    _prefix = "pdf-page"

    def __init__(self, logger: Logger):
        self._logger = logger

    def create_directory(self, directory: Path) -> None:
        if not directory:
            raise ValueError("Must provide directory.")
        directory.mkdir(exist_ok=True, parents=True)

    def store_dir(self, base_dir: Path, file_hash: str):
        if not base_dir:
            raise ValueError("Must provide base directory.")
        if not file_hash:
            raise ValueError("Must provide file hash.")
        dir_1 = file_hash[:2]
        dir_2 = file_hash[:15]
        return base_dir / dir_1 / dir_2

    def details_file(self, pdf_file: Path):
        return pdf_file.parent / "pdf-details.json"

    def identify_file(self, base_dir: Path, file_hash: str):
        return self.store_dir(base_dir, file_hash) / "pdf-identify.json"

    def pdf_info_file(self, base_dir: Path, file_hash: str):
        return self.store_dir(base_dir, file_hash) / "pdf-info.txt"

    def pdf_text_file(self, base_dir: Path, file_hash: str):
        return self.store_dir(base_dir, file_hash) / "pdf-text.txt"

    def pdf_images_path(self, base_dir: Path, file_hash: str):
        # the pdftopng exe will add the suffix '-nnnnnn.png' (6 x 'n' - page number digits)
        name = self._prefix
        return self.store_dir(base_dir, file_hash) / name

    def pdf_page_image_file(self, base_dir: Path, file_hash: str, page: int):
        name = f"{self._prefix}-{page:06}.png"
        return self.store_dir(base_dir, file_hash) / name

    def pdf_page_prepared_file(
        self, base_dir: Path, file_hash: str, threshold: int, page: int
    ):
        name = f"{self._prefix}-{page:06}-a1-th-{threshold:03}.png"
        return self.store_dir(base_dir, file_hash) / name

    def pdf_page_ocr_file(
        self, base_dir: Path, file_hash: str, threshold: int, page: int
    ):
        name = f"{self._prefix}-{page:06}-b1-th-{threshold:03}.png"
        return self.store_dir(base_dir, file_hash) / name

    def pdf_page_text_file(
        self, base_dir: Path, file_hash: str, threshold: int, page: int
    ):
        name = f"{self._prefix}-{page:06}-b1-th-{threshold:03}.csv"
        return self.store_dir(base_dir, file_hash) / name
