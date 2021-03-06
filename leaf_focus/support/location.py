from logging import Logger
from pathlib import Path

from leaf_focus.pdf.images.item import Item as ImageItem


class Location:
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
        dir_1 = file_hash[0:2]
        dir_2 = file_hash[0:15]
        return base_dir / dir_1 / dir_2

    def details_file(self, pdf_file: Path):
        return pdf_file.parent / "pdf-details.json"

    def identify_file(self, base_dir: Path, file_hash: str):
        return self.store_dir(base_dir, file_hash) / "pdf-identify.json"

    def info_file(self, base_dir: Path, file_hash: str):
        return self.store_dir(base_dir, file_hash) / "pdf-info.json"

    def pdf_text_file(self, base_dir: Path, file_hash: str):
        return self.store_dir(base_dir, file_hash) / "pdf-text.txt"

    def pdf_images_path(self, base_dir: Path, file_hash: str):
        # the pdftopng exe will add the suffix '-nnnnnn.png'
        # (6 x 'n' - page number digits)
        return self.store_dir(base_dir, file_hash) / "pdf-page"

    def pdf_page_image_file(self, base_dir: Path, file_hash: str, page: int):
        name = ImageItem.build(page=page, suffix=".png")
        return self.store_dir(base_dir, file_hash) / name

    def pdf_page_prepared_file(
        self, base_dir: Path, file_hash: str, page: int, threshold: int
    ):
        name = ImageItem.build(page, suffix=".png", variety="prep", threshold=threshold)
        return self.store_dir(base_dir, file_hash) / name

    def pdf_page_ocr_file(
        self, base_dir: Path, file_hash: str, page: int, threshold: int
    ):
        name = ImageItem.build(page, suffix=".png", variety="ocr", threshold=threshold)
        return self.store_dir(base_dir, file_hash) / name

    def pdf_page_text_file(
        self, base_dir: Path, file_hash: str, page: int, threshold: int
    ):
        name = ImageItem.build(page, suffix=".csv", variety="text", threshold=threshold)
        return self.store_dir(base_dir, file_hash) / name
