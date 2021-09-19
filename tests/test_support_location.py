import logging

from leaf_focus.support.location import Location
from tests.base_test import BaseTest


class TestSupportLocation(BaseTest):

    _new_dir = "new-dir-01"

    def test_create_directory(self, tmp_path):
        location = Location(logging.getLogger())
        created_dir = tmp_path / self._new_dir
        assert not created_dir.exists()
        location.create_directory(created_dir)
        assert created_dir.exists()

    def test_store_dir(self, tmp_path, example1_pdf_hash, example1_pdf_hash_dir):
        location = Location(logging.getLogger())
        base_dir = tmp_path
        fh = example1_pdf_hash
        dh = example1_pdf_hash_dir
        store_dir = location.store_dir(base_dir, fh)
        assert store_dir == base_dir / dh

    def test_details_file(self, tmp_path):
        location = Location(logging.getLogger())
        pdf_file = tmp_path / self._new_dir / "file.pdf"
        details_file = location.details_file(pdf_file)
        assert details_file == tmp_path / self._new_dir / "pdf-details.json"

    def test_identify_file(self, tmp_path, example1_pdf_hash, example1_pdf_hash_dir):
        location = Location(logging.getLogger())
        base_dir = tmp_path
        fh = example1_pdf_hash
        dh = example1_pdf_hash_dir
        store_dir = location.identify_file(base_dir, fh)
        assert store_dir == base_dir / dh / "pdf-identify.json"

    def test_info_file(self, tmp_path, example1_pdf_hash, example1_pdf_hash_dir):
        location = Location(logging.getLogger())
        base_dir = tmp_path
        fh = example1_pdf_hash
        dh = example1_pdf_hash_dir
        store_dir = location.info_file(base_dir, fh)
        assert store_dir == base_dir / dh / "pdf-info.json"

    def test_pdf_text_file(self, tmp_path, example1_pdf_hash, example1_pdf_hash_dir):
        location = Location(logging.getLogger())
        base_dir = tmp_path
        fh = example1_pdf_hash
        dh = example1_pdf_hash_dir
        store_dir = location.pdf_text_file(base_dir, fh)
        assert store_dir == base_dir / dh / "pdf-text.txt"

    def test_pdf_images_path(self, tmp_path, example1_pdf_hash, example1_pdf_hash_dir):
        location = Location(logging.getLogger())
        base_dir = tmp_path
        fh = example1_pdf_hash
        dh = example1_pdf_hash_dir
        store_dir = location.pdf_images_path(base_dir, fh)
        assert store_dir == base_dir / dh / "pdf-page"

    def test_pdf_page_image_file(
        self, tmp_path, example1_pdf_hash, example1_pdf_hash_dir
    ):
        page = 2
        name = "pdf-page-000002.png"
        location = Location(logging.getLogger())
        base_dir = tmp_path
        fh = example1_pdf_hash
        dh = example1_pdf_hash_dir
        store_dir = location.pdf_page_image_file(base_dir, fh, page)
        assert store_dir == base_dir / dh / name

    def test_pdf_page_prepared_file(
        self, tmp_path, example1_pdf_hash, example1_pdf_hash_dir
    ):
        page = 2
        threshold = 190
        name = "pdf-page-000002-prep-th-190.png"
        loc = Location(logging.getLogger())
        bd = tmp_path
        fh = example1_pdf_hash
        dh = example1_pdf_hash_dir
        store_dir = loc.pdf_page_prepared_file(bd, fh, page, threshold)
        assert store_dir == bd / dh / name

    def test_pdf_page_ocr_file(
        self, tmp_path, example1_pdf_hash, example1_pdf_hash_dir
    ):
        page = 2
        threshold = 9
        name = "pdf-page-000002-ocr-th-009.png"
        loc = Location(logging.getLogger())
        base_dir = tmp_path
        fh = example1_pdf_hash
        dh = example1_pdf_hash_dir
        store_dir = loc.pdf_page_ocr_file(base_dir, fh, page, threshold)
        assert store_dir == base_dir / dh / name

    def test_pdf_page_text_file(
        self, tmp_path, example1_pdf_hash, example1_pdf_hash_dir
    ):
        page = 2
        threshold = 190
        name = "pdf-page-000002-text-th-190.csv"
        loc = Location(logging.getLogger())
        base_dir = tmp_path
        fh = example1_pdf_hash
        dh = example1_pdf_hash_dir
        store_dir = loc.pdf_page_text_file(base_dir, fh, page, threshold)
        assert store_dir == base_dir / dh / name
