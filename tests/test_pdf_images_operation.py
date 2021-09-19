import logging

from leaf_focus.pdf.images.operation import Operation
from tests.base_test import BaseTest


class TestPdfImagesOperation(BaseTest):
    def test_instance(self, tmp_path):
        tmp_file = tmp_path / "example"
        tmp_file.touch()
        Operation(logging.getLogger(), tmp_path, tmp_file)
