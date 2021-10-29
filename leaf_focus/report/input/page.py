from dataclasses import field
from typing import TYPE_CHECKING, Iterable
from pathlib import Path
from typing import Optional

from attr import dataclass

from leaf_focus.pdf.text.component import Component
from leaf_focus.report.input.line import Line
from leaf_focus.ocr.recognise.item import Item as OcrItem

if TYPE_CHECKING:
    from leaf_focus.report.input.document import Document


@dataclass
class Page:
    index: int
    """The raw index of this page."""

    document: "Document"
    """The document that contains this page."""

    lines: Optional[list[Line]] = field(default_factory=list)
    """The lines in the page."""

    items: Optional[list[OcrItem]] = field(default_factory=list)
    """The recognised items in a line."""

    @classmethod
    def load(cls, document_dir: Path, document: "Document") -> Iterable["Page"]:
        """Load pages of a document."""
        text_path = document_dir / "pdf-text.txt"
        if not text_path.exists():
            return []
        for index, raw_lines in enumerate(Component.read(text_path)):
            # TODO: load ocr text
            page = Page(
                index=index,
                document=document,
            )
            lines = Line.load(raw_lines, page)
            page.lines = list(lines)
            yield page

    def __str__(self):
        return f"page {self.index} with {len(self.lines)} lines"
