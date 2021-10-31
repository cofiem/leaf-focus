import re
from enum import Enum
from logging import Logger
from typing import Iterable, Optional

from leaf_focus.report.input.dates import Dates
from leaf_focus.report.input.document import Document
from leaf_focus.report.input.line import Line
from leaf_focus.report.input.text import Text
from leaf_focus.report.output.correction import Correction
from leaf_focus.report.output.item import Item as ReportItem
from leaf_focus.report.output.line_parser import LineParser
from leaf_focus.report.output.match import Match
from leaf_focus.report.output.outcome import Outcome
from leaf_focus.report.output.section import Section


class ParseResult(Enum):
    UNKNOWN = 0
    MATCH = 1
    NO_MATCH = 2


class Parse:
    def __init__(
        self,
        logger: Logger,
        parsers: Iterable[LineParser],
        sections: Iterable[Section],
        corrections: Iterable[Correction],
        urls: Iterable[dict],
    ):
        self._logger = logger
        self._parsers = list(parsers)
        self._sections = list(sections)
        self._corrections = list(corrections)
        self._urls = list(urls)
        self._dates = Dates()
        self._text = Text()
        self._allow_overwrite = [
            "page_number",
            "unknown_date",
        ]
        self._temporary_entries = [
            "page_number",
            "processed_date",
            "signed_date",
            "received_date",
            "change_type_addition",
            "change_type_deletion",
            "unknown_date",
        ]

    def documents(self, docs: Iterable[Document]) -> Iterable[ReportItem]:
        for doc in docs:
            items = self.document(doc)
            for item in items:
                yield item

    def document(self, document: Document) -> Iterable[ReportItem]:
        """Parse a document into report items."""

        self._logger.info(
            f"Processing document '{document.short_hash}' "
            f"with {len(document.pages)} pages."
        )

        lines = self.document_lines(document)

        line_info = []
        previous_line_type = None
        for line in lines:
            if not line.text:
                # ensure empty lines have already been filtered
                raise ValueError()

            outcome = self.find_def(line.text)

            # the explanatory notes document is
            # not a register of interests
            if (
                outcome
                and outcome.parser
                and outcome.parser.value == "EXPLANATORY NOTES"
            ):
                return []

            if not outcome.is_match and previous_line_type != "table-header":
                outcome.requires_check = True

            # record the outcome for the current line
            line_info.append(Match(line, outcome))

            if outcome and outcome.parser and outcome.parser.line_type:
                previous_line_type = outcome.parser.line_type

        # check
        # requires_check = [i for i in line_info if i.outcome.requires_check]
        # if requires_check:
        #     pass

        # use the line info to build the ReportItems
        for item in self.report_items(document, line_info):
            yield item

    def document_lines(self, document: Document) -> Iterable[Line]:
        """Select the page lines to use."""

        for page in document.pages:
            # if the ocr items are available, use them
            if page.items:
                for index, text in enumerate(page.items_text_iter()):
                    yield Line(index=index, text=text, page=page)
            else:
                # otherwise use the embedded text lines
                for line in page.lines:
                    yield line

    def find_def(self, text: str) -> Outcome:
        """Check to see if the definition's first entry matches the line."""
        found = []
        for parser in self._parsers:
            is_match, extracted = parser.match(text)
            if is_match:
                found.append(Outcome(is_match=True, parser=parser, extracted=extracted))

        found_count = len(found)
        if found_count < 1:
            return Outcome(is_match=False)

        if found_count == 1:
            return found[0]

        if found_count > 1:
            return Outcome(is_match=False)

    def report_items(self, document: Document, items: Iterable[Match]):
        """Convert lines from a document into report items."""

        collected = {}
        current_table = None
        previous_line_type = None
        current_change_type = "addition"
        current_register_section = None
        for item in items:
            page = item.line.page.index
            line = item.line.index + 1
            outcome = item.outcome

            # skip the line if it requires checking
            # it likely is unusable
            if outcome.requires_check:
                self._logger.warning(f"Skipping line that requires check {str(item)}.")
                continue

            # get the current line type
            if outcome and outcome.parser:
                current_line_type = outcome.parser.line_type
            else:
                current_line_type = None

            # only interested in line type of 'line'
            # if it has extracted data
            extracted = outcome.extracted if outcome.is_match else {}
            if outcome.is_match and not extracted and current_line_type == "line":
                previous_line_type = current_line_type
                continue

            # if this line is a table header
            # and the previous line was not a table header
            # set the current line as the table header
            if (
                current_line_type == "table-header"
                and previous_line_type != "table-header"
            ):
                current_table = item
                previous_line_type = current_line_type

                # remove temporary entries
                for temporary in self._temporary_entries:
                    if temporary in collected:
                        del collected[temporary]

                continue

            # set the previous line type
            if outcome and outcome.parser:
                previous_line_type = current_line_type

            # if this is a multi-line header
            # don't try to use the header as a table row
            if current_line_type == "table-header":
                continue

            # Add the data extracted from the line
            # to the collected data
            for k, v in extracted.items():
                if not k or not v:
                    continue
                self.report_item_extract(k, v, item, collected)

            # update change_type
            if extracted.get("change_type_addition"):
                current_change_type = "addition"
            if extracted.get("change_type_deletion"):
                current_change_type = "deletion"

            # extract table row from line that is not a match
            # only if there is a currently active table header
            if not outcome.is_match and current_table:
                extracted = self.page_table(current_table, item)

                if current_table.outcome.parser.group == "alteration":
                    extracted, current_register_section = self.alteration(
                        current_table, item, current_register_section, extracted
                    )
                else:
                    current_register_section = current_table.outcome.parser.group

                extracted["register_section"] = current_register_section
                extracted["pdf_page"] = page
                extracted["pdf_line"] = line
                extracted["change_type"] = current_change_type

                report_item = self.report_item(document, {**collected, **extracted})
                if report_item.is_valid:
                    yield report_item
                else:
                    self._logger.warning(f"Invalid report item {str(report_item)}.")

                # remove temporary entries
                for temporary in self._temporary_entries:
                    if temporary in collected:
                        del collected[temporary]

    def report_item_extract(self, key: str, value: dict, item: Match, collected: dict):
        extracted_value = self._text.norm_text(value["value"])
        extracted_value = self._text.collapse_spaces(extracted_value)
        extracted_value = self.corrections(extracted_value)

        if (
            extracted_value
            and key not in self._allow_overwrite
            and key in collected
            and extracted_value != collected[key]
        ):
            self._logger.warning(
                f"Unexpected new value for '{key}' "
                f"'{collected[key]}' -> '{extracted_value}' for {str(item)}."
            )
            return

        if key and value and key not in collected:
            collected[key] = extracted_value

    def page_table(self, header: Match, row: Match) -> dict:
        header_dict = header.outcome.extracted
        header_sorted = sorted(header_dict.items(), key=lambda x: x[1]["span"][0])
        header_count = len(header_dict)
        header_keys = ", ".join([k for k, v in header_sorted])
        row_text = row.line.text
        text_len = len(row_text)

        # Note: if there are only two columns,
        # and the first column is form_who,
        # then there may only be one header,
        # and it may not line up with the start of the second column.
        # In this situation, the start of the second column can be found by
        # finding the first double space, then moving to the next non-whitespace
        # character.

        if header_count == 2 and header_sorted[0][0] == "form_who" and "  " in row_text:
            start_index = row_text.index("  ")
            match = re.search(r"\S", row_text[start_index:])
            if match:
                second_header_start = start_index + match.span()[0]
                existing_end = header_sorted[1][1]["span"][1]
                header_sorted[1][1]["span"] = (second_header_start, existing_end)

        extracted = {}
        for index, (k, v) in enumerate(header_sorted):
            next_index = index + 1
            is_last_header = next_index >= header_count

            start = v["span"][0]
            if is_last_header:
                end = text_len
            else:
                next_header_start = header_sorted[next_index][1]["span"][0]
                end = min([next_header_start, text_len])
            is_last_col = end >= text_len
            cell_text = row_text[start:end]

            # check the table row split worked as expected
            if not is_last_header and not is_last_col and cell_text[-2:] != "  ":
                self._logger.warning(
                    f"Skipping table row '{row_text}' ({header_keys})."
                )
                continue

            # add the column key and value
            extracted[k] = cell_text.strip(r" .-\/_")

            # if this is the last column that can be extracted
            # due to the row text length
            # there is no point trying to extract later columns
            if is_last_col:
                break

        return extracted

    def report_item(self, doc: Document, data: dict) -> ReportItem:
        processed_date = self._text.norm_text(data.get("processed_date"))
        processed_date = self._dates.parse(processed_date)

        signed_date = self._text.norm_text(data.get("signed_date"))
        signed_date = self._dates.parse(signed_date)

        item = ReportItem(
            pdf_path=doc.pdf_path,
            pdf_hash_type=doc.pdf_hash_type,
            pdf_hash_value=doc.pdf_hash_value,
            pdf_created_date=doc.pdf_created_date,
            pdf_modified_date=doc.pdf_modified_date,
            pdf_downloaded_date=doc.pdf_downloaded_date,
            website_modified_date=doc.website_modified_date,
            pdf_url=doc.pdf_url,
            referrer_url=doc.referrer_url,
            pdf_page=data.get("pdf_page"),
            pdf_line=data.get("pdf_line"),
            processed_date=processed_date,
            signed_date=signed_date,
            assembly=doc.assembly,
            last_name=data.get("last_name"),
            first_name=data.get("first_name"),
            state_or_territory=data.get("state_or_territory"),
            electorate=data.get("electorate"),
            register_section=data.get("register_section"),
            change_type=data.get("change_type"),
            form_who=data.get("form_who"),
            form_name=data.get("form_name"),
            form_activity=data.get("form_activity"),
            form_participation=data.get("form_participation"),
            form_location=data.get("form_location"),
        )
        return item

    def alteration(
        self,
        current_table: Match,
        item: Match,
        current_register_section: str,
        extracted: dict,
    ) -> tuple[dict, str]:
        if not current_table:
            return extracted, current_register_section
        if not current_table.outcome:
            return extracted, current_register_section
        if not current_table.outcome.parser:
            return extracted, current_register_section
        if current_table.outcome.parser.group != "alteration":
            return extracted, current_register_section

        raw_register_section = extracted.get("register_section")
        if raw_register_section:
            register_section = None
            for section in self._sections:
                if raw_register_section in section.names:
                    register_section = section.name

            if not register_section:
                self._logger.warning(
                    f"Unknown alteration group '{raw_register_section}'."
                )
                register_section = None

        else:
            register_section = current_register_section

        general_details = extracted.get("general_details")
        if register_section == "travel-hospitality":
            extracted = {"form_participation": general_details}
        elif register_section == "real-estate":
            extracted = {"form_participation": general_details}
        elif register_section == "liabilities":
            extracted = {"form_participation": general_details}
        elif register_section == "gifts":
            extracted = {"form_participation": general_details}
        elif register_section == "organisation-memberships":
            extracted = {"form_name": general_details}
        elif register_section == "other-income":
            extracted = {"form_participation": general_details}
        elif register_section == "shareholdings":
            extracted = {"form_name": general_details}
        elif register_section == "directorships":
            extracted = {"form_name": general_details}
        elif register_section == "other-assets":
            extracted = {"form_participation": general_details}
        else:
            # TODO
            extracted = {"form_participation": item.line.text}

        return extracted, register_section

    def corrections(self, value: str):
        for correction in self._corrections:
            result = correction.regex.sub(correction.replace, value)
            if result != value:
                return result
        return value
