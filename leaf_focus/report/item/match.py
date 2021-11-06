from dataclasses import dataclass

from leaf_focus.report.item.line import Line
from leaf_focus.report.item.outcome import Outcome


@dataclass
class Match:
    line: Line
    outcome: Outcome

    def __str__(self):
        doc_short_hash = self.line.page.document.short_hash
        page_index = self.line.page.index
        line_index = self.line.index
        line_text = self.line.text
        msgs = [
            f"doc {doc_short_hash}",
            f"page {page_index}",
            f"line {line_index}",
            f"outcome {self.outcome}",
            f"text '{line_text}'",
        ]
        return " ".join(msgs)
