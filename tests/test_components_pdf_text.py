import logging
from pathlib import Path

import pytest

from leaf_focus.components.pdf.text import Text


class TestComponentsPdfText:
    def test_no_exe(self):
        with pytest.raises(ValueError, match="Must supply exe file."):
            Text(logging.getLogger(), None)

    def test_exe_not_found(self):
        path = "this-path-does-not-exist"
        with pytest.raises(
            FileNotFoundError,
            match=f"Exe file does not exist '{path}'.",
        ):
            Text(logging.getLogger(), Path(path))
