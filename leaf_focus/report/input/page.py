import typing
from pathlib import Path
from typing import Optional


from leaf_focus.report.input.line import Line
from leaf_focus.ocr.recognise.item import Item as OcrItem

if typing.TYPE_CHECKING:
    from leaf_focus.report.input.document import Document


class Page:
    index: int
    """The raw index of this page."""

    number: Optional[int]
    """The provided page number."""

    lines: Optional[list[Line]]
    """The lines in the page."""

    items: Optional[list[OcrItem]]
    """The recognised items in a line."""

    document: "Document"
    """The document that contains this page."""

    @classmethod
    def load(cls, document_dir: Path, document: "Document") -> typing.Iterable["Page"]:
        """Load pages of a document."""
        # TODO: load pages
        return []
