from dataclasses import dataclass
from typing import Iterable

from leaf_focus.report.input.line import Line
from leaf_focus.report.output.definition_table import DefinitionTable
from leaf_focus.report.output.outcome import OutcomeTableHeader, Outcome


@dataclass
class DefinitionAlterationTable(DefinitionTable):
    register_section: list[str]
    general_details: list[str]

    @classmethod
    def load(cls, items: list[dict]) -> "DefinitionAlterationTable":
        raw = {
            "register_section": [],
            "general_details": [],
        }
        for item in items:
            for key, value in item.items():
                if value is None:
                    continue

                if isinstance(value, list):
                    raw[key].extend(value)
                else:
                    raw[key].append(value)

        return DefinitionAlterationTable(**raw)

    def header_match(self, line: Line) -> Iterable[OutcomeTableHeader]:
        return self._header_match(
            line,
            register_section=self.register_section,
            general_details=self.general_details,
        )

    def body(self, line: Line, outcome: Outcome) -> Outcome:
        another_header_row = self._header_rows(line, outcome)
        if another_header_row:
            return Outcome(
                match_type=OutcomeType.ALTERATION_TABLE,
                is_match=False,
                index=outcome.index,
                table_headers=outcome.table_headers,
            )

        # parse the table body
        return Outcome(
            match_type=OutcomeType.ALTERATION_TABLE,
            is_match=True,
            index=outcome.index,
            table_headers=outcome.table_headers,
        )

    def __str__(self):
        raw = {
            "register_section": self.register_section,
            "general_details": self.general_details,
        }
        return "; ".join(f"{k}={v}" for k, v in raw.items() if v)
