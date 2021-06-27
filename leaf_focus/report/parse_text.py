import logging
import re
from configparser import ConfigParser
from datetime import datetime

from leaf_focus.download.items.pdf_item import PdfItem
from leaf_focus.ocr.found_text import FoundText
from leaf_focus.report.report_item import ReportItem


class ParseText:
    def __init__(self, logger: logging.Logger):
        self._logger = logger

        # import contextualSpellCheck
        # import spacy
        #
        # # self._nlp_gpu = spacy.prefer_gpu()
        # self._nlp = spacy.load("en_core_web_lg")
        # contextualSpellCheck.add_to_pipe(self._nlp)
        # print(self._nlp.pipe_names)

    def start(
        self,
        item: PdfItem,
        text_info: dict,
        text_extracted: list[str],
        text_found: list[list[FoundText]],
    ):
        results = []  # type: list[ReportItem]

        result = self._populate_info(item, text_info)
        results.append(result)

        # text_extracted (all text from a pdf file)
        # TODO

        return results

    def _populate_info(self, item: PdfItem, text_info: dict):
        # item details (for a pdf file)
        category = item["category"]
        is_rep = category == "member"
        is_sen = category == "senator"
        if not is_rep and not is_sen:
            raise ValueError(f"Unrecognised category '{category}'.")

        last_updated = self._get_date(item["last_updated"])
        referrer = item["referrer"]
        url = item["url"]

        # path = Path(item["path"])

        name = item["name"]
        ignore_names = ["Resolutions of the House", "Explanatory notes"]
        if name in ignore_names:
            return None
        (
            person_full,
            person_last,
            person_first,
            person_electorate,
            person_state,
            person_title,
        ) = self._parse_name(name)

        # text_info (from a pdf file)
        config = ConfigParser(converters={"date": self._get_date})
        section = "main"
        config.read_dict({section: text_info})

        # get the pdf info   fallback=None
        # pdf_unknown1 = config.get(section, "unknown1", fallback=None)
        # pdf_unknown2 = config.get(section, "unknown2", fallback=None)
        # pdf_unknown3 = config.get(section, "unknown3", fallback=None)
        #
        # pdf_title = config.get(section, "Title", fallback=None)
        # pdf_subject = config.get(section, "Subject", fallback=None)
        # pdf_keywords = config.get(section, "Keywords", fallback=None)
        # pdf_author = config.get(section, "Author", fallback=None)
        # pdf_creator = config.get(section, "Creator", fallback=None)
        # pdf_producer = config.get(section, "Producer", fallback=None)

        pdf_date_created = config.getdate(section, "CreationDate", fallback=None)
        pdf_date_modified = config.getdate(section, "ModDate", fallback=None)
        pdf_is_tagged = config.getboolean(section, "Tagged", fallback=None)
        pdf_form = config.get(section, "Form", fallback=None)
        pdf_page_count = config.getint(section, "Pages", fallback=None)
        pdf_is_encrypted = config.getboolean(section, "Encrypted", fallback=None)

        pdf_pagesize = config.get(section, "Page size", fallback=None)
        (
            pdf_width,
            pdf_height,
            pdf_measure,
            pdf_format,
            pdf_rotation,
        ) = self._parse_page_size(pdf_pagesize)

        pdf_filesize = config.get(section, "File size", fallback=None)
        pdf_size_amount, pdf_size_suffix = self._parse_file_size(pdf_filesize)

        pdf_is_optimized = config.getboolean(section, "Optimized", fallback=None)
        pdf_version = config.get(section, "PDF version", fallback=None)

        result = ReportItem(
            # basic info
            category=category,
            parliament_number="",
            # urls
            page_url=url,
            referrer_url=referrer,
            # person info
            person_full=person_full,
            person_last=person_last,
            person_first=person_first,
            person_electorate=person_electorate,
            person_state=person_state,
            person_title=person_title,
            # dates
            date_created_web=None,
            date_updated_web=last_updated,
            date_created_doc=pdf_date_created,
            date_updated_doc=pdf_date_modified,
            # pdf metadata
            pdf_is_tagged=pdf_is_tagged,
            pdf_form=pdf_form,
            pdf_page_count=pdf_page_count,
            pdf_is_encrypted=pdf_is_encrypted,
            pdf_pagesize=pdf_pagesize,
            pdf_width=pdf_width,
            pdf_height=pdf_height,
            pdf_measure=pdf_measure,
            pdf_format=pdf_format,
            pdf_rotation=pdf_rotation,
            pdf_filesize=pdf_filesize,
            pdf_size_amount=pdf_size_amount,
            pdf_size_suffix=pdf_size_suffix,
            pdf_is_optimized=pdf_is_optimized,
            pdf_version=pdf_version,
        )
        self._logger.info(f"Info for '{result.person_full}' from '{result.page_url}'.")
        return result

    def _find_text(self, text: str, to_find: list[str]):
        if text in to_find:
            return True, "whole"
        if any([text.startswith(t) for t in to_find]):
            return True, "start"
        if any([text.endswith(t) for t in to_find]):
            return True, "end"
        if any([text in t for t in to_find]):
            return True, "contains"
        return False, None

    def _extract(self, lines: list[list[FoundText]]):
        # TODO
        find_text = [
            ("self", "", ["self"]),
            ("spouse", "", ["spouse"]),
            ("children", "", ["dependent", "children"]),
            ("last_name", "", ["surname", "please print"]),
            ("first_name", self._match_first_name, ["other names"]),
            ("electorate", "", ["electoral division", "electoral division state"]),
            (
                "companies",
                "",
                [
                    "shareholdings in public and private companies",
                    "the name of the company",
                ],
            ),
        ]
        for line_index, line_item in enumerate(lines):
            text = " ".join([i.text for i in line_item]).lower()

            for name, func, match in find_text:
                is_match, where_match = self._find_text(text, match)
                if not is_match:
                    continue

    def _match_first_name(
        self,
        lines: list[list[FoundText]],
        line_index: int,
        line_item: list[FoundText],
        text: str,
        where_match: str,
    ):
        # TODO
        a = 1

    def _get_date(self, value: str):
        value = self._norm_text(value)

        if len(value) == 24 and value[8] == " ":
            # for days 1 - 9, pad with 0
            value = value[:8] + "0" + value[9:]

        date_seps = [" and ", " to "]
        for date_sep in date_seps:
            if date_sep in value:
                start_index = value.index(date_sep) + len(date_sep)
                value = value[start_index:]

        extras = ["(alterations only)", "(statements only)"]
        for extra in extras:
            if extra in value:
                value = value.replace(extra, "").strip()

        # too many spaces: remove all spaces
        if ":" not in value and value.count(" ") > 2:
            value = value.replace(" ", "")

        patterns = [
            # examples: 'Tue Jan 10 12:30:24 2017', 'Tue Apr  9 12:05:10 2019'
            "%a %b %d %H:%M:%S %Y",
            # examples: '28 March 2019'
            "%d %B %Y",
            # examples: '28 Mar 2019'
            "%d %b %Y",
            # examples: '28March 2019'
            "%d%B %Y",
            # examples: '28Mar 2019'
            "%d %b %Y",
            # examples: '28March2019'
            "%d%B%Y",
            # examples: '28Mar2019'
            "%d%b%Y",
            # examples: 'Last updated 7 May 2018'
            "Last updated %d %B %Y",
        ]
        for pattern in patterns:
            try:
                parsed = datetime.strptime(value, pattern)
                formatted = parsed.isoformat()
                return formatted
            except ValueError:
                continue
        if not value:
            return None
        raise ValueError(value)

    def _parse_page_size(self, value: str):
        value = self._norm_text(value)

        # examples: '595 x 841 pts (rotated 0 degrees)',
        # '595.32 x 841.92 pts (A4) (rotated 0 degrees)'
        pattern = re.compile(
            r"^(?P<width>[^ ]+) x (?P<height>[^ ]+) (?P<measure>[^ ]+) (\((?P<format>[^ ]+)\) )?\(rotated (?P<rotation>[^ ]+) degrees\)$"
        )
        match = pattern.fullmatch(value)
        if match:
            result = match.groupdict()
            return (
                float(result.get("width", "0")),
                float(result.get("height", "0")),
                result.get("measure"),
                result.get("format"),
                float(result.get("rotation", "0")),
            )
        if not value:
            return None, None, None, None, None
        raise ValueError(value)

    def _parse_file_size(self, value: str):
        value = self._norm_text(value)

        pattern = re.compile(r"^(?P<amount>[^ ]+) (?P<suffix>[^ ]+)$")
        match = pattern.fullmatch(value)
        if match:
            result = match.groupdict()
            return (
                int(result.get("amount")),
                result.get("suffix"),
            )
        if not value:
            return None, None
        raise ValueError(value)

    def _parse_name(self, value: str):
        value = self._norm_text(value)

        # fix known issues
        issues = {
            "Member Eden-Monaro NSW": "Member for Eden-Monaro, NSW",
            "Member for Griffith,": "Member for Griffith, QLD",
            "Member for Braddon TAS": "Member for Braddon, TAS",
            "Member for Maribyrnong. VIC": "Member for Maribyrnong, VIC",
            "Senator forTasmania": "Senator for Tasmania",
        }
        for find, fix in issues.items():
            if value.strip().endswith(find):
                value = value.replace(find, fix)

        # member titles
        member_titles = "|".join(
            [
                "AM, CSC, Mr",
                "Professor",
                "The Hon Dr",
                "The Hon Mrs",
                "The Hon Ms",
                "The Hon Mr",
                "The Hon",
                "The Hom",
                "the hon",
                "Hon Dr",
                "Hon Mrs",
                "Hon Ms",
                "Hon Mr",
                "Hon",
                "Mrs",
                "Dr",
                "Ms",
                "Mr",
            ]
        )

        # member electorate prefixes
        member_prefixes = "|".join(
            [
                "Former Member for",
                "Member for",
                "Member",
                "for",
            ]
        )

        # senator titles
        senator_titles = "|".join(
            [
                "Senator the Hon",
                "Senator",
            ]
        )

        patterns = [
            # member
            re.compile(
                fr"^(?P<last1>[^,]+),? (?P<title1>{member_titles}) (?P<first1>[^,]+), (({member_prefixes}) )((?P<electorate1>.+), (?P<state1>.+)|(?P<electorate2>[^,]+))?$"
            ),
            # senate
            re.compile(
                fr"^(?P<last1>.+[^,]+), (?P<title1>{senator_titles}) (?:(?P<first1>.+)( - (Senator for) (?P<state1>.+))|(?P<first2>.+))$"
            ),
        ]
        for pattern in patterns:
            match = pattern.fullmatch(value)
            if match:
                result = match.groupdict()
                return (
                    value,
                    self._norm_name(result.get("last1")),
                    self._norm_name(result.get("first1") or result.get("first2")),
                    result.get("electorate2") or result.get("electorate1"),
                    self._norm_state(result.get("state1")),
                    result.get("title1"),
                )
        if not value or not self._norm_name(value):
            return value, None, None, None, None, None
        raise ValueError(value)

    def _norm_state(self, value: str):
        if not value:
            return None
        alpha = re.compile(f"[^a-zA-Z ]")
        value = alpha.sub("", value).lower()
        known = {
            "act": "ACT",
            "australian capital territory": "ACT",
            "new south wales": "NSW",
            "northern territory": "NT",
            "nsw": "NSW",
            "nt": "NT",
            "qld": "QLD",
            "queensland": "QLD",
            "sa": "SA",
            "south australia": "SA",
            "tas": "TAS",
            "tasmania": "TAS",
            "vic": "VIC",
            "victoria": "VIC",
            "wa": "WA",
            "waw": "WA",
            "western australia": "WA",
        }
        return known[value]

    def _norm_text(self, value: str):
        value = value.strip() if value else ""
        replacements = {
            "–": "-",
            "—": "-",
            "\xa0": " ",  # \xa0 is NBSP
            "  ": " ",
        }
        for find, replace in replacements.items():
            value = value.replace(find, replace)
        return value

    def _norm_name(self, value: str):
        if value.endswith(", AO"):
            return value[0:-4]
        if value.endswith(" AO"):
            return value[0:-3]

        replacements = [
            "(PDF",
            "( PDF",
            "(",
            ")",
            "Vol 1 -",
            "Volume 1 -",
            "Vol 1 ",
            "Vol 2 -",
            "Volume 2 -",
            "Vol 2 ",
        ]
        for replace in replacements:
            value = value.replace(replace, "")

        return value.strip()


#  – Senator for New South Wales
# Spender, Senator Duncan
