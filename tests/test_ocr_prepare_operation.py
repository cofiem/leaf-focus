import logging

from leaf_focus.ocr.prepare.operation import Operation


class TestOcrPrepareOperation:
    def test_instance(self, tmp_path):
        Operation(logging.getLogger(), tmp_path)
