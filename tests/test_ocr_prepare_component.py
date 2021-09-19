import logging
from pathlib import Path

import pytest

from leaf_focus.ocr.prepare.component import Component
from leaf_focus.pdf.images.component import Component as ImageComponent
from tests.base_test import BaseTest


class TestOcrPrepareComponent(BaseTest):
    def test_instance(self):
        Component(logging.getLogger())

    @pytest.mark.needs_exe
    def test_create_read(self, tmp_path, exe_pdf_image):
        c_image = ImageComponent(logging.getLogger(), exe_pdf_image)
        c = Component(logging.getLogger())

        image_prefix_path = Path(tmp_path, "image")
        c_image.create(self.example1_path(".pdf"), image_prefix_path)

        image = Path(str(image_prefix_path) + "-000001.png")
        assert image.exists()
        assert Path(str(image_prefix_path) + "-000001.png").exists()

        threshold_path = Path(tmp_path, "threshold.png")
        c.threshold(image, threshold_path, 100)

        assert threshold_path.exists()
        assert threshold_path.stat().st_size == 5517
        assert image.stat().st_size != threshold_path.stat().st_size
