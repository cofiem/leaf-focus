import re
from dataclasses import dataclass
from typing import Optional, Iterable

from leaf_focus.report.input.line import Line
from leaf_focus.report.output.definition_table import DefinitionTable
from leaf_focus.report.output.outcome import OutcomeTableHeader, Outcome


@dataclass
class DefinitionSectionTable(DefinitionTable):
    form_who: list[str]
    form_name: Optional[list[str]]
    form_activity: Optional[list[str]]
    form_participation: Optional[list[str]]
    form_location: Optional[list[str]]

    @classmethod
    def load(cls, items: list[dict]) -> "DefinitionSectionTable":
        raw = {
            "form_who": [],
            "form_name": [],
            "form_activity": [],
            "form_participation": [],
            "form_location": [],
        }
        for item in items:
            for key, value in item.items():
                if value is None:
                    continue

                if isinstance(value, list):
                    raw[key].extend(value)
                else:
                    raw[key].append(value)

        return DefinitionSectionTable(**raw)

    @property
    def _page_number_re(self):
        return re.compile(r"^\s{40,}\d+$")

    @property
    def column_count(self):
        cols = [
            self.form_who,
            self.form_name,
            self.form_activity,
            self.form_participation,
            self.form_location,
        ]
        items = [i for i in cols if i]
        return len(items)

    @property
    def other_column_name(self):
        """
        For a two-column section table,
        get the name of the column
        that is not the 'who'. column.
        """
        cols = {
            "form_name": self.form_name,
            "form_activity": self.form_activity,
            "form_participation": self.form_participation,
            "form_location": self.form_location,
        }
        for name, value in cols.items():
            if value:
                return name

        raise ValueError()

    def header_match(self, line: Line) -> Iterable[OutcomeTableHeader]:
        return self._header_match(
            line,
            form_who=self.form_who,
            form_name=self.form_name,
            form_activity=self.form_activity,
            form_participation=self.form_participation,
            form_location=self.form_location,
        )

    def body(self, line: Line, outcome: Outcome) -> Outcome:
        # a line with only a number, which is 40 spaces or more in,
        # is most likely a page number
        if self._page_number_re.match(line.text):
            return Outcome(
                is_match=False,
                index=outcome.index,
                table_headers=outcome.table_headers,
            )

        another_header_row = self._header_rows(line, outcome)
        if another_header_row:
            return Outcome(
                is_match=True,
                index=outcome.index,
                table_headers=outcome.table_headers,
            )

        # parse the table body
        opts_self = ["Self"]
        opts_partner = ["Spouse/", "partner"]
        opts_dependent = ["Dependent", "children"]
        opts_text = [j for i in [opts_self, opts_partner, opts_dependent] for j in i]
        width = max(len(i) for i in opts_text)
        opts_valid = opts_text + [width * " "]

        form_who = None
        for opt_valid in opts_valid:
            if line.text.startswith(opt_valid):
                form_who = opt_valid.strip()
                break

        if form_who is None:
            return Outcome(
                is_match=True,
                index=outcome.index,
                table_headers=outcome.table_headers,
            )

        # A two column table might have headers that do not line up with the body.
        # A three or more column table will have headers that line up.
        form_who_len = len(form_who)
        column_count = self.column_count
        if column_count < 2:
            raise ValueError()

        elif column_count == 2:
            col_name = self.other_column_name
            col_value = line.text[form_who_len:].strip()
            return Outcome(
                is_match=True,
                index=outcome.index,
                table_headers=outcome.table_headers,
                dict_data={"form_who": form_who, col_name: col_value},
            )

        else:
            return self.row(line, outcome)

    def row(self, line: Line, outcome: Outcome) -> Outcome:
        data = sorted(
            [i for i in outcome.table_headers if i.index is not None],
            key=lambda x: x.index,
        )
        result = {}
        line_len = len(line.text)
        data_len = len(data)
        for entry_index, entry in enumerate(data):
            name = entry.name
            start_index = entry.index
            if not entry.text or start_index is None:
                continue

            next_entry_index = entry_index + 1
            if data_len <= next_entry_index:
                index_end = line_len
            else:
                next_start_index = data[next_entry_index].index
                if next_start_index:
                    index_end = next_start_index
                else:
                    index_end = line_len

            if line_len >= start_index:
                result[name] = line.text[start_index:index_end].strip()
            else:
                result[name] = ""

        return Outcome(
            is_match=True,
            index=outcome.index,
            table_headers=outcome.table_headers,
            dict_data=result,
        )

    def __str__(self):
        raw = {
            "form_who": self.form_who,
            "form_name": self.form_name,
            "form_activity": self.form_activity,
            "form_participation": self.form_participation,
            "form_location": self.form_location,
        }
        return "; ".join(f"{k}={v}" for k, v in raw.items() if v)
