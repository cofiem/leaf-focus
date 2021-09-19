import logging
import pytest
from pathlib import Path

from leaf_focus.pdf.text.component import Component
from tests.base_test import BaseTest


class TestPdfTextComponent(BaseTest):
    def test_no_exe(self):
        with pytest.raises(ValueError, match="Must supply exe file."):
            Component(logging.getLogger(), None)

    def test_exe_not_found(self):
        path = "this-path-does-not-exist"
        with pytest.raises(
            FileNotFoundError,
            match=f"Exe file does not exist '{path}'.",
        ):
            Component(logging.getLogger(), Path(path))

    def test_found_exe(self, tmp_path):
        tmp_file = tmp_path / "example"
        tmp_file.touch()
        Component(logging.getLogger(), tmp_file)

    @pytest.mark.needs_exe
    def test_create_read(self, tmp_path, exe_pdf_text):
        c = Component(logging.getLogger(), exe_pdf_text)

        text_path = Path(tmp_path, "text.txt")
        c.create(self.example1_path(".pdf"), text_path)
        text = c.read(text_path)

        assert text == [
            [
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod "
                "tempor incididunt ut labore",
                "et dolore magna aliqua.",
                "Enim sit amet venenatis urna cursus eget nunc scelerisque viverra.",
                "Aliquet lectus proin nibh nisl.",
                "Curabitur vitae nunc sed velit dignissim sodales.",
                "Tellus id interdum velit laoreet id donec.",
            ]
        ]
