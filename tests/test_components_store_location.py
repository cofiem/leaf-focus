import logging
import tempfile
from pathlib import Path

from leaf_focus.components.location import Location


class TestComponentsStoreLocation:

    _new_dir = "new-dir-01"
    _file_hash = "2d6f1f7a2558f6415e120453356a62ccbc6b27a66d0ef1253eb6610f5f679cc7"
    _file_hash_1 = "2d"
    _file_hash_2 = "2d6f1f7a2558f64"
    _dir_hash = Path(_file_hash_1) / _file_hash_2

    def test_create_directory(self):
        location = Location(logging.getLogger())
        with tempfile.TemporaryDirectory() as d:
            created_dir = Path(d) / self._new_dir
            assert not created_dir.exists()
            location.create_directory(created_dir)
            assert created_dir.exists()

    def test_store_dir(self):
        location = Location(logging.getLogger())
        with tempfile.TemporaryDirectory() as d:
            base_dir = Path(d)
            store_dir = location.store_dir(base_dir, self._file_hash)
            assert store_dir == base_dir / self._dir_hash

    def test_details_file(self):
        location = Location(logging.getLogger())
        with tempfile.TemporaryDirectory() as d:
            pdf_file = Path(d) / self._new_dir / "file.pdf"
            details_file = location.details_file(pdf_file)
            assert details_file == Path(d) / self._new_dir / "pdf-details.json"

    def test_identify_file(self):
        location = Location(logging.getLogger())
        with tempfile.TemporaryDirectory() as d:
            base_dir = Path(d)
            store_dir = location.identify_file(base_dir, self._file_hash)
            assert store_dir == base_dir / self._dir_hash / "pdf-identify.json"

    def test_info_file(self):
        location = Location(logging.getLogger())
        with tempfile.TemporaryDirectory() as d:
            base_dir = Path(d)
            store_dir = location.info_file(base_dir, self._file_hash)
            assert store_dir == base_dir / self._dir_hash / "pdf-info.json"

    def test_pdf_info_file(self):
        location = Location(logging.getLogger())
        with tempfile.TemporaryDirectory() as d:
            base_dir = Path(d)
            store_dir = location.pdf_info_file(base_dir, self._file_hash)
            assert store_dir == base_dir / self._dir_hash / "pdf-info.txt"

    def test_pdf_text_file(self):
        location = Location(logging.getLogger())
        with tempfile.TemporaryDirectory() as d:
            base_dir = Path(d)
            store_dir = location.pdf_text_file(base_dir, self._file_hash)
            assert store_dir == base_dir / self._dir_hash / "pdf-text.txt"

    def test_pdf_images_path(self):
        location = Location(logging.getLogger())
        with tempfile.TemporaryDirectory() as d:
            base_dir = Path(d)
            store_dir = location.pdf_images_path(base_dir, self._file_hash)
            assert store_dir == base_dir / self._dir_hash / "pdf-page"

    def test_pdf_page_image_file(self):
        page = 2
        name = "pdf-page-000002.png"
        location = Location(logging.getLogger())
        with tempfile.TemporaryDirectory() as d:
            base_dir = Path(d)
            fh = self._file_hash
            dh = self._dir_hash
            store_dir = location.pdf_page_image_file(base_dir, fh, page)
            assert store_dir == base_dir / dh / name

    def test_pdf_page_prepared_file(self):
        page = 2
        threshold = 190
        name = "pdf-page-000002-prep-th-190.png"
        loc = Location(logging.getLogger())
        with tempfile.TemporaryDirectory() as d:
            bd = Path(d)
            fh = self._file_hash
            dh = self._dir_hash
            store_dir = loc.pdf_page_prepared_file(bd, fh, page, threshold)
            assert store_dir == bd / dh / name

    def test_pdf_page_ocr_file(self):
        page = 2
        threshold = 9
        name = "pdf-page-000002-ocr-th-009.png"
        loc = Location(logging.getLogger())
        with tempfile.TemporaryDirectory() as d:
            base_dir = Path(d)
            fh = self._file_hash
            dh = self._dir_hash
            store_dir = loc.pdf_page_ocr_file(base_dir, fh, page, threshold)
            assert store_dir == base_dir / dh / name

    def test_pdf_page_text_file(self):
        page = 2
        threshold = 190
        name = "pdf-page-000002-text-th-190.csv"
        loc = Location(logging.getLogger())
        with tempfile.TemporaryDirectory() as d:
            base_dir = Path(d)
            fh = self._file_hash
            dh = self._dir_hash
            store_dir = loc.pdf_page_text_file(base_dir, fh, page, threshold)
            assert store_dir == base_dir / dh / name
