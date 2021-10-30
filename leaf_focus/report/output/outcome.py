from dataclasses import dataclass
from typing import Optional

from leaf_focus.report.output.line_parser import LineParser


@dataclass
class OutcomeTableHeader:
    name: str
    text: list[str]
    index: Optional[int]

    def __str__(self):
        return f"{self.name}:{self.index}"


@dataclass
class Outcome:
    is_match: bool
    parser: Optional[LineParser] = None
    extracted: Optional[dict] = None
    requires_check: bool = False

    def clone(self):
        """Create a new Outcome with the same values."""
        return Outcome(
            is_match=self.is_match,
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
            "data": self.extracted or {},
        }
        return ", ".join([f"{k}: {v}" for k, v in result.items()])
