import logging
from pathlib import Path

import pytest

from leaf_focus.components.pdf.info import Info


class TestComponentsPdfInfo:
    def test_no_exe(self):
        with pytest.raises(ValueError, match="Must supply exe file."):
            Info(logging.getLogger(), None)

    def test_exe_not_found(self):
        path = "this-path-does-not-exist"
        with pytest.raises(
            FileNotFoundError,
            match=f"Exe file does not exist '{path}'.",
        ):
            Info(logging.getLogger(), Path(path))
