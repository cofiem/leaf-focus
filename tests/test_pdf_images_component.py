import logging
import pytest
from pathlib import Path
from leaf_focus.pdf.images.component import Component
from tests.base_test import BaseTest


class TestPdfImagesComponent(BaseTest):
    def test_no_exe(self):
        with pytest.raises(ValueError, match="Must supply exe file."):
            Component(logging.getLogger(), None)

    def test_exe_not_found(self):
        path = "this-path-does-not-exist"
        with pytest.raises(
            FileNotFoundError,
            match=f"Exe file does not exist '{path}'.",
        ):
            Component(logging.getLogger(), Path(path))

    def test_found_exe(self, tmp_path):
        tmp_file = tmp_path / "example"
        tmp_file.touch()
        Component(logging.getLogger(), tmp_file)

    @pytest.mark.needs_exe
    def test_create_read(self, tmp_path, exe_pdf_image):
        c = Component(logging.getLogger(), exe_pdf_image)

        image_prefix_path = Path(tmp_path, "image")
        c.create(self.example1_path(".pdf"), image_prefix_path)

        expected = Path(str(image_prefix_path) + "-000001.png")
        assert expected.exists()
        assert expected.stat().st_size == 21703
        assert Path(str(image_prefix_path) + "-000001.png").exists()
        assert not Path(str(image_prefix_path) + "-000002.png").exists()
