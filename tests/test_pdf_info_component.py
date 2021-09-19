import logging
import pytest
from pathlib import Path

from leaf_focus.pdf.info.component import Component
from leaf_focus.pdf.info.item import Item
from tests.base_test import BaseTest


class TestPdfInfoComponent(BaseTest):
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
    def test_create_read(self, tmp_path, exe_pdf_info):
        c = Component(logging.getLogger(), exe_pdf_info)

        info_path = Path(tmp_path, "info.json")
        c.create(self.example1_path(".pdf"), info_path)
        info = Item.load_json(info_path)

        assert info.entries["Creator"] == "Microsoft® Word for Microsoft 365"
        assert info.entries["Producer"] == "Microsoft® Word for Microsoft 365"
        assert info.entries["CreationDate"] == "Sat Sep 18 22:43:28 2021"
        assert info.entries["ModDate"] == "Sat Sep 18 22:43:28 2021"
        assert info.entries["Tagged"] == "yes"
        assert info.entries["Form"] == "none"
        assert info.entries["Pages"] == "1"
        assert info.entries["Encrypted"] == "no"
        assert (
            info.entries["Page size"] == "595.32 x 841.92 pts (A4) (rotated 0 degrees)"
        )
        assert info.entries["File size"] == "40135 bytes"
        assert info.entries["Optimized"] == "no"
        assert info.entries["PDF version"] == "1.7"
