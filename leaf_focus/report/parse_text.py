import logging
from pathlib import Path

from leaf_focus.download.items.pdf_item import PdfItem

from leaf_focus.ocr.found_text import FoundText


class ParseText:
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def start(self, input_items_path: Path):
        if not input_items_path.exists() or not input_items_path.is_dir():
            msg = f"Could not find input items dir '{input_items_path}'."
            self._logger.error(msg)
            raise ValueError(msg)

        result = []
        for item_file in input_items_path.glob("items*.csv"):

            for item in PdfItem.load(item_file):
                input_dir = Path(item.path).parent

                for csv_file in input_dir.glob("*.csv"):
                    found_items = list(FoundText.load(csv_file))
                    lines = self._text_service.order_text_lines(found_items)
                    self._extract(lines)
        return result

    def _find_text(self, text: str, to_find: list[str]):
        if text in to_find:
            return True, "whole"
        if any([text.startswith(t) for t in to_find]):
            return True, "start"
        if any([text.endswith(t) for t in to_find]):
            return True, "end"
        if any([text in t for t in to_find]):
            return True, "contains"
        return False, None

    def _extract(self, lines: list[list[FoundText]]):
        # TODO
        find_text = [
            ("self", "", ["self"]),
            ("spouse", "", ["spouse"]),
            ("children", "", ["dependent", "children"]),
            ("last_name", "", ["surname", "please print"]),
            ("first_name", self._match_first_name, ["other names"]),
            ("electorate", "", ["electoral division", "electoral division state"]),
            (
                "companies",
                "",
                [
                    "shareholdings in public and private companies",
                    "the name of the company",
                ],
            ),
        ]
        for line_index, line_item in enumerate(lines):
            text = " ".join([i.text for i in line_item]).lower()

            for name, func, match in find_text:
                is_match, where_match = self._find_text(text, match)
                if not is_match:
                    continue

    def _match_first_name(
        self,
        lines: list[list[FoundText]],
        line_index: int,
        line_item: list[FoundText],
        text: str,
        where_match: str,
    ):
        # TODO
        a = 1
