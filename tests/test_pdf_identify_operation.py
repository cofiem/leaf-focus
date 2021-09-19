import logging

from leaf_focus.pdf.identify.operation import Operation
from tests.base_test import BaseTest


class TestPdfIdentifyOperation(BaseTest):
    def test_instance(self, tmp_path):
        Operation(logging.getLogger(), tmp_path)
