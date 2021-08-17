import logging
from pathlib import Path

import pytest

from leaf_focus.components.pdf.images import Images


class TestPdfImages:
    def test_no_exe(self):
        with pytest.raises(ValueError, match="Must supply exe file."):
            Images(logging.getLogger(), None)

    def test_exe_not_found(self):
        path = "this-path-does-not-exist"
        with pytest.raises(
            FileNotFoundError,
            match=f"Exe file does not exist '{path}'.",
        ):
            Images(logging.getLogger(), Path(path))
