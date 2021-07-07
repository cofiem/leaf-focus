import logging

from leaf_focus.ocr.found_text import FoundText
from leaf_focus.report.content_item import ContentItem
from leaf_focus.report.metadata_item import MetadataItem
from leaf_focus.report.parse.base import Base
from leaf_focus.report.parse.members_interests_first_page_notes import (
    MembersInterestsFirstPageNotes,
)


class ContentReport:
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._parsers = [
            MembersInterestsFirstPageNotes(),
        ]  # type: list[Base]

    def start(
        self,
        text_info: MetadataItem,
        text_extracted: list[list[str]],
        text_found: list[list[FoundText]],
    ) -> list[ContentItem]:
        """Parse the contents of a pdf file into structured data."""

        # ensure extracted and found have the same number of pages
        if len(text_extracted) != len(text_found):
            extra_items = [[] for _ in range((len(text_extracted) - len(text_found)))]
            text_found.extend(extra_items)

        # examine the page contents and pull out the information we need
        content_items = []
        empty_pages = []
        shared_data = {}
        for page_index, (extracted_page, found_page) in enumerate(
            zip(text_extracted, text_found)
        ):
            page_number = page_index + 1

            max_char_count = 0
            has_extracted_content = False
            for extracted_line in extracted_page:
                if not extracted_line:
                    continue
                char_count = len(extracted_line)
                if char_count > max_char_count:
                    max_char_count = char_count
                    has_extracted_content = True

            if max_char_count < 1 and not has_extracted_content and not found_page:
                empty_pages.append(page_number)
                self._logger.debug(
                    f"Page {page_number} is empty for '{str(text_info)}'."
                )
                continue

            # try each parser until one returns success or all have been tried
            for parser in self._parsers:
                page_items = parser.run(
                    text_info,
                    extracted_page,
                    found_page,
                    page_number,
                    shared_data,
                )
                if not page_items:
                    continue
                for page_item in page_items:
                    if page_item.has_content():
                        content_items.extend(page_items)

        if len(empty_pages) > 0:
            self._logger.info(
                f"Found {len(empty_pages)} empty pages in '{str(text_info)}'."
            )
        return content_items
