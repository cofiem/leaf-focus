import logging
from pathlib import Path

import pytest

from leaf_focus.pdf.identify.component import Component
from tests.base_test import BaseTest


class TestPdfIdentifyComponent(BaseTest):
    def test_path_not_found(self):
        path = "this-path-does-not-exist"
        with pytest.raises(
            FileNotFoundError,
            match=f"Path does not exist '{path}'.",
        ):
            identify = Component(logging.getLogger())
            identify.file_hash(Path(path))

    @pytest.mark.parametrize("suffix", [".docx", ".pdf", ".png", ".txt"])
    def test_file_hash(self, suffix):
        identify = Component(logging.getLogger())
        actual = identify.file_hash(self.example1_path(suffix))
        assert actual == self.example1_hash(suffix)
