from typing import Iterable

from leaf_focus.report.input.line import Line
from leaf_focus.report.output.outcome import OutcomeTableHeader, Outcome


class DefinitionTable:
    @classmethod
    def load(cls, items: list[dict]) -> "DefinitionTable":
        raise NotImplementedError()

    def _header_match(self, line: Line, **kwargs) -> list[OutcomeTableHeader]:
        if not kwargs:
            return []

        kwargs_count = len([k for k, v in kwargs.items() if v])
        headers = []
        for name, texts in kwargs.items():
            if len(texts) < 1:
                continue

            for text in texts:
                if len(texts) > 1:
                    pass
                if text == "":
                    headers.append(OutcomeTableHeader(name=name, text=text, index=0))
                    break
                elif text is None:
                    break
                elif text not in line.text:
                    return []
                else:
                    headers.append(
                        OutcomeTableHeader(
                            name=name, text=text, index=line.text.index(text)
                        )
                    )
                    break
        if len(headers) != kwargs_count:
            return []
        return headers

    def _header_rows(self, line: Line, outcome: Outcome) -> bool:
        # if the headers occupy more than one line, ensure the headers exist
        # return the table header data again
        has_header = False
        for entry in outcome.table_headers:
            text = entry.text
            entry_index = entry.index
            if len(text) < (outcome.index + 1):
                continue
            expected_header = text[outcome.index]
            actual_header = line.text[entry_index:]
            if not actual_header.startswith(expected_header):
                raise ValueError(
                    f"Expected header '{expected_header}' "
                    f"at pos {entry_index} in line '{line.text}'."
                )
            has_header = True

        return has_header
