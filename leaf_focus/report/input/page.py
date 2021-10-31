import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

from leaf_focus.ocr.recognise.item import Item as OcrItem
from leaf_focus.pdf.images.item import Item as ImageItem
from leaf_focus.pdf.text.component import Component
from leaf_focus.report.input.line import Line

if TYPE_CHECKING:
    from leaf_focus.report.input.document import Document


@dataclass
class Page:
    index: int
    """The raw index of this page."""

    document: "Document"
    """The document that contains this page."""

    lines: list[Line] = field(default_factory=list)
    """The lines in the page."""

    items: list[OcrItem] = field(default_factory=list)
    """The recognised items in a line."""

    @classmethod
    def load(cls, document_dir: Path, document: "Document") -> Iterable["Page"]:
        """Load pages of a document."""
        text_path = document_dir / "pdf-text.txt"
        if not text_path.exists():
            return []

        # load ocr text
        pattern = ImageItem._pattern
        item_pages = {}
        for item_path in document_dir.glob("pdf-page-*text*.csv"):
            match = pattern.match(item_path.stem)
            if not match:
                continue
            item_page = int(match.group("page") or 0, 10)
            if item_page < 1:
                continue
            item_pages[item_page] = OcrItem.load(item_path)

        # load embedded text lines
        for index, raw_lines in enumerate(Component.read(text_path)):
            page = Page(index=index, document=document)
            lines = Line.load(raw_lines, page)
            page.lines = list(lines)

            page_num = index + 1
            if page_num in item_pages:
                page.items = list(item_pages[page_num])
            yield page

    def items_line_count(self) -> int:
        """Get the number of lines provided by ocr items."""
        return max([i.line_number for i in self.items if i.line_number])

    def items_line(self, line_num: int) -> Iterable[OcrItem]:
        """Get the ocr items for a line."""
        line_items = [i for i in self.items if i.line_number == line_num]
        sorted_items = sorted(line_items, key=lambda x: x.line_order)
        return sorted_items

    def items_text(self, line_num: int) -> str:
        """
        Get the ocr text for a line spaced
        according to item positions.
        """
        sorted_items = self.items_line(line_num)
        est_char_width = 11
        text = ""
        for item in sorted_items:
            offset_chars = math.floor(item.top_left_x / est_char_width)
            text_chars = len(text)

            # ignore that offset_chars might sometimes be smaller than text_chars
            # each phrase does not overlap and
            # has to be to the right by at least one space
            if offset_chars > text_chars:
                text += " " * (offset_chars - text_chars)
            else:
                text += " "

            text += item.text
        return text

    def items_text_iter(self, start_num: int = 1) -> Iterable[str]:
        end_line = self.items_line_count() + 1
        for line_num in range(start_num, end_line):
            yield self.items_text(line_num)

    def __str__(self):
        return f"page {self.index} with {len(self.lines)} lines"
