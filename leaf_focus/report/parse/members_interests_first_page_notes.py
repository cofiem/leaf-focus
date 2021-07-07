from datetime import datetime

from leaf_focus.ocr.found_text import FoundText
from leaf_focus.report.content_item import ContentItem
from leaf_focus.report.metadata_item import MetadataItem
from leaf_focus.report.parse.base import Base
from leaf_focus.report.parse.compare_words import CompareWords


class MembersInterestsFirstPageNotes(Base):

    header = [
        [
            "registry",
            "of",
            "members",
            "interests",
        ],
        [
            "register",
            "of",
            "members",
            "interests",
        ],
        [
            "statement",
            "of",
            "registrable",
            "interests",
        ],
        [
            "46th",
            "parliament",
        ],
        [
            "returning",
            "members",
            "are",
            "to",
            "declare",
            "interests",
            "as",
            "at",
            "the",
            "date",
            "of",
            "dissolution",
            "of",
        ],
        [
            "the",
            "house",
            "in",
            "the",
            "45th",
            "parliament",
            "11",
            "april",
            "2019",
            "and",
            "alterations",
            "since",
            "the",
        ],
        [
            "date",
            "of",
            "dissolution",
        ],
        [
            "newly",
            "elected",
            "members",
            "are",
            "to",
            "declare",
            "interests",
            "as",
            "at",
            "the",
            "date",
            "of",
            "election",
        ],
        [
            "18",
            "may",
            "2019",
            "and",
            "alterations",
            "since",
            "the",
            "date",
            "of",
            "election",
        ],
    ]
    notes = [
        ["notes"],
        [
            "1",
            "it",
            "is",
            "suggested",
            "that",
            "the",
            "accompanying",
            "explanatory",
            "notes",
            "be",
            "read",
            "before",
            "this",
            "statement",
            "is",
        ],
        [
            "completed",
        ],
        [
            "2",
            "the",
            "information",
            "which",
            "you",
            "are",
            "required",
            "to",
            "provide",
            "is",
            "contained",
            "in",
            "resolutions",
            "agreed",
            "to",
            "by",
            "the",
        ],
        [
            "house",
            "of",
            "representatives",
            "on",
            "9",
            "october",
            "1984",
            "amended",
            "13",
            "february",
            "1986",
            "22",
            "october",
            "1986",
        ],
        [
            "30",
            "november",
            "1988",
            "9",
            "november",
            "1994",
            "6",
            "november",
            "2003",
            "and",
            "13",
            "february",
            "2008",
            "it",
            "consists",
            "of",
        ],
        [
            "the",
            "members",
            "registrable",
            "interests",
            "and",
            "the",
            "registrable",
            "interests",
            "of",
            "which",
            "the",
            "member",
            "is",
            "aware",
        ],
        [
            "a",
            "of",
            "the",
            "members",
            "spouse",
            "and",
            "b",
            "of",
            "any",
            "children",
            "who",
            "are",
            "wholly",
            "or",
            "mainly",
            "dependent",
            "on",
            "the",
        ],
        [
            "member",
            "for",
            "support.",
            "for",
            "the",
            "definition",
            "of",
            "dependent",
            "children",
            "see",
            "the",
            "introduction",
            "to",
            "the",
        ],
        [
            "explanatory",
            "notes",
        ],
        [
            "3",
            "if",
            "there",
            "is",
            "insufficient",
            "space",
            "on",
            "this",
            "form",
            "for",
            "the",
            "information",
            "you",
            "are",
            "required",
            "to",
            "provide,",
            "you",
            "may",
        ],
        [
            "attach",
            "additional",
            "pages",
            "for",
            "that",
            "purpose.",
            "please",
            "date",
            "and",
            "initial",
            "each",
            "page",
            "of",
            "any",
            "attachment",
        ],
    ]

    def run(
        self,
        text_info: MetadataItem,
        text_extracted: list[str],
        text_found: list[FoundText],
        page_number: int,
        shared_data: dict,
    ):
        date_processed = None
        first_names = []
        last_names = []
        division = []
        state = []

        # if text_found:
        #     raise ValueError(
        #         {
        #             "text_info": text_info,
        #             "text_extracted": text_extracted,
        #             "text_found": text_found,
        #             "page_number": page_number,
        #             "shared_data": shared_data,
        #         }
        #     )

        for line in text_extracted:
            line_norm = self._normalise_str(line)

            if not line_norm:
                continue

            if date_processed is None:
                date_processed = self._get_processed_date(line_norm)
                if date_processed:
                    continue

            line_words = self._line_words(line_norm)

            comparisons = []
            for compare in [self.header, self.notes]:
                compare_result = CompareWords(line_words, compare)
                if compare_result.result:
                    comparisons.append(compare_result)

            if any([i.percentage for i in comparisons]):
                continue

            # pick the content
            containers = [
                ("FAMILY NAME", last_names),
                ("GIVEN NAMES", first_names),
                ("please print", first_names),
            ]
            starts_with_match = False
            for starts_with, container in containers:
                starts_with_match = line_norm.startswith(starts_with)
                if not starts_with_match:
                    continue
                starts_with_len = len(starts_with)
                line_new = line_norm[starts_with_len:].strip()
                if line_new:
                    container.append(line_new)
                break

            if starts_with_match:
                continue

            if line_norm.startswith("ELECTORAL DIVISION"):
                line_new = line_norm[18:].strip()
                division, state = line_new.split("STATE")
                division = [division.strip()]
                state = [state.strip()]
                continue

            a = 1

        return [
            ContentItem(
                page_number=page_number,
                doc_url=text_info.page_url,
                date_processed_text=date_processed.isoformat()
                if date_processed
                else None,
                first_names=" ".join(first_names) if first_names else None,
                last_names=" ".join(last_names) if last_names else None,
                electorate=" ".join(division) if division else None,
                state=self._normalise.state(" ".join(state)) if state else None,
            )
        ]

    def _get_processed_date(self, line: str):
        try:
            return datetime.strptime(line, "PROCESSED %d %b %Y")
        except ValueError:
            return None
