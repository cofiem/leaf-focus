from pathlib import Path
from typing import Optional

import pytest

from leaf_focus.pdf.images.item import Item
from tests.base_test import BaseTest


class TestPdfImagesItem(BaseTest):
    @pytest.mark.parametrize(
        "expected,page,suffix,variety,threshold",
        [
            ("pdf-page-000001-text-th-190.csv", 1, ".csv", "text", 190),
            ("pdf-page-000156-ocr-th-188.png", 156, ".png", "ocr", 188),
            ("pdf-page-002050-prep-th-001.png", 2050, ".png", "prep", 1),
            ("pdf-page-002050-prep.png", 2050, ".png", "prep", None),
            ("pdf-page-000054.png", 54, ".png", None, None),
        ],
    )
    def test_build(
        self,
        expected: str,
        page: int,
        suffix: str,
        variety: Optional[str],
        threshold: Optional[int],
    ):
        actual = Item.build(page, suffix, variety, threshold)
        assert actual == expected

    @pytest.mark.parametrize(
        "expected,path",
        [
            (
                Item(Path("pdf-page-000001-text-th-190.csv"), 1, 190, "text"),
                Path("pdf-page-000001-text-th-190.csv"),
            ),
            (
                Item(Path("pdf-page-000156-ocr-th-188.png"), 156, 188, "ocr"),
                Path("pdf-page-000156-ocr-th-188.png"),
            ),
            (
                Item(Path("pdf-page-002050-prep-th-001.png"), 2050, 1, "prep"),
                Path("pdf-page-002050-prep-th-001.png"),
            ),
            (
                Item(Path("pdf-page-002050-prep.png"), 2050, None, "prep"),
                Path("pdf-page-002050-prep.png"),
            ),
            (
                Item(Path("pdf-page-000054.png"), 54, None, None),
                Path("pdf-page-000054.png"),
            ),
        ],
    )
    def test_read(self, expected: Item, path: Path):
        actual = Item.read(path)
        assert actual == expected
