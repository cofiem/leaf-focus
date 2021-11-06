from dataclasses import dataclass
from typing import Optional

from leaf_focus.report.item.line_parser import LineParser


@dataclass
class Outcome:
    is_match: bool
    match_count: int
    parser: Optional[LineParser] = None
    extracted: Optional[dict] = None
    text: Optional[str] = None

    def clone(self):
        """Create a new Outcome with the same values."""
        return Outcome(
            is_match=self.is_match,
            match_count=self.match_count,
            parser=self.parser,
            extracted={**(self.extracted or {})},
        )

    def as_no_match(self):
        """Create a new Outcome that is not a match."""
        outcome = self.clone()
        outcome.is_match = False
        return outcome

    def __str__(self):
        result = {
            "match": "yes" if self.is_match else "no",
            "count": self.match_count,
            "data": self.extracted or {},
        }
        return ", ".join([f"{k}: {v}" for k, v in result.items()])
