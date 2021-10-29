from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass


if TYPE_CHECKING:
    from leaf_focus.report.input.page import Page


@dataclass
class Line:
    index: int
    """The raw index of this line."""

    number: Optional[int]
    """The provided line number."""

    text: str
    """The raw text for this line."""

    section: Optional[str]
    """The section of the page."""

    page: "Page"
    """The page that contains this line."""
