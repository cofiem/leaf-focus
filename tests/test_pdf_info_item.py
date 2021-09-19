from leaf_focus.pdf.info.item import Item
from tests.base_test import BaseTest


class TestPdfInfoItem(BaseTest):
    def test_round_trip(self, tmp_path):
        base_path = tmp_path

        expected = [
            Item(pdf_path=base_path / "1.csv", entries={"one": "1", "two": "2"}),
            Item(pdf_path=base_path / "2.csv", entries={"three": "3", "four": "4"}),
        ]

        items_path = base_path / "items.csv"

        assert not items_path.is_file()

        Item.save_csv(items_path, expected)

        assert items_path.is_file()

        actual = list(Item.load_csv(items_path))

        assert actual == expected
