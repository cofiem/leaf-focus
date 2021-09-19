import logging

import pytest

from leaf_focus.ocr.recognise.component import Component


class TestOcrRecogniseComponent:
    @pytest.mark.slow
    def test_instance(self):
        Component(logging.getLogger())
