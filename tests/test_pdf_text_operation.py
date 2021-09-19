import logging
from leaf_focus.pdf.text.operation import Operation
from tests.base_test import BaseTest


class TestPdfTextOperation(BaseTest):
    def test_instance(self, tmp_path):
        tmp_file = tmp_path / "example"
        tmp_file.touch()
        Operation(logging.getLogger(), tmp_path, tmp_file)
