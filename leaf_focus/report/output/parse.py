import re
from enum import Enum
from logging import Logger
from typing import Iterable, Optional

from leaf_focus.report.input.document import Document
from leaf_focus.report.input.line import Line
from leaf_focus.report.output.definition import (
    Definition,
    DefinitionLine,
    DefinitionTable,
)
from leaf_focus.report.output.item import Item as ReportItem
from leaf_focus.report.output.match import Match


class ParseResult(Enum):
    UNKNOWN = 0
    MATCH = 1
    NO_MATCH = 2


class Parse:
    def __init__(self, logger: Logger, definitions: Iterable[Definition]):
        self._logger = logger
        self._definitions = list(definitions)
        self._collapse_spaces_re = re.compile(r"\s+")
        self._page_number_re = re.compile(r"^\s{40,}\d+$")

    def documents(self, docs: Iterable[Document]) -> Iterable[ReportItem]:
        for doc in docs:
            item = self.document(doc)
            if item:
                yield item

    def document(self, document: Document):
        """Parse a document into report items."""
        lines = (line for page in document.pages for line in page.lines)

        # TODO: how to integrate line items?
        # items = (item for page in document.pages for item in page.items )

        results = []

        current_def = None
        current_parsed = None
        current_index = 0
        for line in lines:
            if not line.text:
                continue

            if current_def:
                current_def, parsed = self.next_def(
                    line, current_def, current_index, current_parsed
                )

            if not current_def:
                current_index = 0
                current_def, current_parsed = self.find_def(line)
                parsed = current_parsed

            if not current_def:
                raise ValueError(line)

            # self.process_def(current_def, current_index, line)

            results.append(Match(line, current_def, current_index, parsed))

            # increment the current index
            current_index += 1

        return []

    def _collapse_spaces(self, value: str) -> str:
        return self._collapse_spaces_re.sub(" ", value)

    def find_def(self, line: Line):
        """Check to see if the definition's first entry matches the line."""
        for definition in self._definitions:
            def_lines = definition.lines
            def_table = definition.table

            if def_lines:
                data = self.line_def(def_lines[0], line)
                if data:
                    return definition, data

            elif def_table:
                data = self.table_header_match(line, def_table)
                if data:
                    return definition, data

            else:
                # TODO: parse table_generic
                raise ValueError("Definition has no lines or table.")

        raise ValueError(f"Not definition matched line {line}.")

    def next_def(
        self, line: Line, definition: Definition, index: int, data: list[dict]
    ):
        def_lines = definition.lines
        def_table = definition.table
        if def_lines and len(def_lines) < (index + 1):
            return None, None

        if def_lines:
            def_line = def_lines[index]
            data = self.line_def(def_line, line)
            if data:
                return definition, data
            else:
                return None, None

        if def_table:
            data = self.table_body(line, def_table, index, data)
            if data:
                return definition, data
            else:
                return None, None

        raise ValueError()

    def line_def(self, def_line: DefinitionLine, line: Line):
        if def_line.regex:
            data = self.line_regex_match(line, def_line)
        else:
            data = self.line_value_match(line, def_line)
        return data

    def line_regex_match(
        self, line: Line, definition: DefinitionLine
    ) -> Optional[dict]:
        for def_regex in definition.regexes:
            match = def_regex.match(line.text)
            if match:
                return match.groupdict()

        return None

    def line_value_match(self, line: Line, definition: DefinitionLine) -> bool:
        for def_value in definition.values:
            value = self._collapse_spaces(line.text).strip()
            match = value == def_value
            if match:
                return True

        return False

    def table_header_match(
        self, line: Line, definition: DefinitionTable
    ) -> Optional[list[dict]]:
        result = [
            {
                "name": "form_who",
                "text": definition.form_who,
                "index": None,
            },
            {
                "name": "form_name",
                "text": definition.form_name,
                "index": None,
            },
            {
                "name": "form_activity",
                "text": definition.form_activity,
                "index": None,
            },
            {
                "name": "form_participation",
                "text": definition.form_participation,
                "index": None,
            },
            {
                "name": "form_location",
                "text": definition.form_location,
                "index": None,
            },
        ]
        for item in result:
            texts = item.get("text")
            if len(texts) < 1:
                continue

            for text in texts:
                if len(texts) > 1:
                    pass
                if text == "":
                    item["index"] = 0
                    break
                elif text is None:
                    break
                elif text not in line.text:
                    return None
                else:
                    item["index"] = line.text.index(text)
                    break

        return result

    def table_body(
        self, line: Line, def_table: DefinitionTable, index: int, data: list[dict]
    ):
        # a line with only a number, which is 40 spaces or more in,
        # is most likely a page number
        if self._page_number_re.match(line.text):
            return None

        # if the headers occupy more than one line, ensure the headers exist
        # return the table header data again
        has_header = False
        for entry in data:
            text = entry.get("text")
            entry_index = entry.get("index")
            if len(text) < (index + 1):
                continue
            expected_header = text[index]
            actual_header = line.text[entry_index:]
            if not actual_header.startswith(expected_header):
                raise ValueError(
                    f"Expected header '{expected_header}' "
                    f"at pos {entry_index} in line '{line.text}'."
                )
            has_header = True

        if has_header:
            return data

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
            return None

        # A two column table might have headers that do not line up with the body.
        # A three or more column table will have headers that line up.
        form_who_len = len(form_who)
        column_count = def_table.column_count
        if column_count < 2:
            raise ValueError()

        elif column_count == 2:
            col_name = def_table.other_column_name
            col_value = line.text[form_who_len:].strip()
            return {"form_who": form_who, col_name: col_value}

        else:
            return self.table_row(line, data)

    def table_row(self, line: Line, data: list[dict]):
        data = sorted(
            [i for i in data if i["index"] is not None], key=lambda x: x["index"]
        )
        result = {}
        line_len = len(line.text)
        data_len = len(data)
        for entry_index, entry in enumerate(data):
            name = entry.get("name")
            text = entry.get("text")
            start_index = entry.get("index")
            if not text or start_index is None:
                continue

            next_entry_index = entry_index + 1
            if data_len <= next_entry_index:
                index_end = line_len
            else:
                next_start_index = data[next_entry_index]["index"]
                if next_start_index:
                    index_end = next_start_index
                else:
                    index_end = line_len

            if line_len >= start_index:
                result[name] = line.text[start_index:index_end].strip()
            else:
                result[name] = ""
        return result


# ReportItem(
#                     pdf_path=self.pdf_path,
#                     pdf_hash_type=self.pdf_hash_type,
#                     pdf_hash_value=self.pdf_hash_value,
#                     pdf_created_date=self.pdf_created_date,
#                     pdf_modified_date=self.pdf_modified_date,
#                     pdf_downloaded_date=self.pdf_downloaded_date,
#                     website_modified_date=self.website_modified_date,
#                     pdf_url=self.pdf_url,
#                     referrer_url=self.referrer_url,
#                     pdf_source=None,
#                     processed_date=None,
#                     signed_date=None,
#                     assembly=None,
#                     last_name=None,
#                     first_name=None,
#                     state_or_territory=None,
#                     electorate=None,
#                     register_section=None,
#                     change_type=None,
#                     form_who=None,
#                 )
