from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from leaf_focus.report.input.page import Page


@dataclass
class Line:
    index: int
    """The raw index of this line."""

    text: str
    """The raw text for this line."""

    page: "Page"
    """The page that contains this line."""

    @classmethod
    def load(cls, lines: Iterable[str], page: "Page") -> Iterable["Line"]:
        """Load lines for a page."""
        for index, text in enumerate(lines):
            line = Line(index=index, text=text, page=page)
            yield line

    def __str__(self):
        return f"line {self.index} '{self.text}'"
