import logging

import pytest

from leaf_focus.ocr.recognise.operation import Operation


class TestOcrRecogniseOperation:
    @pytest.mark.slow
    def test_instance(self, tmp_path):
        Operation(logging.getLogger(), tmp_path)
