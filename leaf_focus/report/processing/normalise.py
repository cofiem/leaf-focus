import re
from datetime import date, datetime
from typing import Iterable, Optional

from leaf_focus.report.item.correction import Correction
from leaf_focus.report.item.known_text import KnownText


class Normalise:
    def __init__(
        self, corrections: Iterable[Correction], known_text: Iterable[KnownText]
    ):
        self._known_text = list(known_text)
        self._corrections = list(corrections)

        self._collapse_spaces_re = re.compile(r"\s+")

        # create regex patterns
        self._name_prefixes = []
        self._name_suffixes = []
        self._member_suffixes = []
        self._senator_suffixes = []
        for known_text in self._known_text:
            for name in known_text.names:
                if known_text.category == "name-prefixes":
                    self._name_prefixes.append(name)
                elif known_text.category == "name-suffixes":
                    self._name_suffixes.append(name)
                elif known_text.category == "member-suffixes":
                    self._member_suffixes.append(name)
                elif known_text.category == "senator-suffixes":
                    self._senator_suffixes.append(name)

        self._name_prefixes = "|".join(self._name_prefixes)
        self._name_suffixes = "|".join(self._name_suffixes)
        self._member_suffixes = "|".join(self._member_suffixes)
        self._senator_suffixes = "|".join(self._senator_suffixes)

        pattern_last = r"(?P<last>.+[^,]+)"
        pattern_first = r"(?P<first>[^,]+)"
        pattern_name_prefixes = fr"(?P<prefix>{self._name_prefixes})"
        pattern_name_suffixes = fr"(?P<suffix>{self._name_suffixes})"

        self._pattern_member = (
            re.compile(
                fr"{pattern_last},? *"
                + fr"{pattern_name_prefixes}? *{pattern_first},? *"
                + fr"{pattern_name_suffixes}? *"
                + fr"((?P<membersuffix>{self._member_suffixes}) *)"
                + r"((?P<electorate1>.+), (?P<state1>.+)|(?P<electorate2>[^,]+))?$"
            ),
        )
        self._pattern_senator = (
            re.compile(
                fr"{pattern_last},? *"
                + fr"{pattern_name_prefixes}? *{pattern_first},? *"
                + fr"{pattern_name_suffixes}?"
                + fr"(((?P<senatorsuffix>{self._senator_suffixes}),? *"
                + r"(?P<state1>.+))|(?P<first2>.+))$"
            ),
        )

    def collapse_spaces(self, value: str) -> str:
        """Collapse all instances of multiple consecutive spaces to one space."""
        if not value:
            return ""
        return self._collapse_spaces_re.sub(" ", value)

    def remove_known_prefix(self, value: str, category: str) -> str:
        """Remove the first matching prefix in the given category."""
        for known_text in self._known_text:
            if known_text.category != category:
                continue
            return self.remove_prefix(value, known_text.names)
        return value

    def remove_prefix(self, value: str, prefixes: list[str]) -> str:
        """Remove the first matching prefix from the value."""
        if not value:
            return ""
        for prefix in prefixes:
            if value.startswith(prefix):
                match_len = len(prefix)
                return value[match_len:]
        return value

    def remove_known_suffix(self, value: str, category: str) -> str:
        """Remove the first matching suffix in the given category."""
        if not value:
            return ""
        for known_text in self._known_text:
            if known_text.category != category:
                continue
            return self.remove_suffix(value, known_text.names)
        return value

    def remove_suffix(self, value: str, suffixes: list[str]) -> str:
        """Remove the first matching suffix from the value."""
        if not value:
            return ""
        for suffix in suffixes:
            if value.endswith(suffix):
                match_len = len(suffix)
                return value[0:match_len]
        return value

    def correction_first(self, value: str, category: str):
        """Apply the first correction that makes a change."""
        if not value or not value.strip():
            return ""

        result = value
        for correction in self._corrections:
            if correction.category != category:
                continue
            if not correction.is_regex and correction.find not in result:
                continue
            result = correction.regex.sub(correction.replace, result)
            if result != value:
                return result

        return result

    def correction_all(self, value: str, category: str):
        """Apply the all the corrections."""
        if not value or not value.strip():
            return ""

        result = value
        for correction in self._corrections:
            if correction.category != category:
                continue
            if not correction.is_regex and correction.find not in result:
                continue
            result = correction.regex.sub(correction.replace, result)

        return result

    def date(self, value: str) -> Optional[date]:
        """Parse a date from a string."""
        # if no value, then no date
        if not value:
            return None

        # apply corrections
        value = self.correction_first(value, category="date")
        value = self.correction_first(value, category="generic")
        value = self.collapse_spaces(value)
        value = value.strip()

        # for days 1 - 9, pad with 0
        if len(value) == 24 and value[8] == " ":
            value = value[:8] + "0" + value[9:]

        # if the date contains a separator, which implies multiple dates,
        # use the last date
        date_seps = [" and ", " to ", "and ", "to ", " and", " to"]
        for date_sep in date_seps:
            if date_sep in value:
                start_index = value.index(date_sep) + len(date_sep)
                value = value[start_index:]

        # too many spaces: remove all spaces
        if ":" not in value and value.count(" ") > 2:
            value = value.replace(" ", "")

        # if the value is no longer valid after these changes,
        # no date is available
        if not value:
            return None

        for known_text in self._known_text:
            if known_text.category != "date-formats":
                continue
            for pattern in known_text.names:
                try:
                    parsed = datetime.strptime(value, pattern)
                    result = parsed.date()
                    return result
                except ValueError:
                    continue

        return None
        # raise ValueError(f"Could not parse date '{value}'.")

    def text(self, value: str) -> Optional[str]:
        """Normalise text."""
        result = value
        result = self.correction_all(result, category="generic")
        return result

    def person_name(self, value: str) -> Optional[str]:
        """Normalise a person's name."""
        result = value
        result = self.correction_first(result, category="generic")
        return result

    def pdf_name(self, value: str) -> Optional[str]:
        """Normalise a name from a pdf."""
        result = value
        result = self.correction_all(result, category="pdf-name")
        return result

    def electorate(self, value: str):
        """Normalise an electorate name, which may include a state name."""
        if not value:
            return None
        alpha = re.compile("[^a-zA-Z ]")
        value = alpha.sub("", value).lower()
        known = {}
        result = known.get(value, None)
        if result is None:
            return value
        return result

    # def parse_name(self, value: str):
    #     value = self.norm_text(value)
    #
    #     patterns = []
    #     for pattern in patterns:
    #         match = pattern.fullmatch(value)
    #         if match:
    #             result = match.groupdict()
    #             norm_last, titles_last = self._norm_name(result.get("last1"))
    #             norm_first, titles_first = self._norm_name(
    #                 result.get("first1") or result.get("first2")
    #             )
    #             titles = (
    #                 result.get("title1", "").split(" ") + titles_last + titles_first
    #             )
    #             titles = " ".join(list(OrderedDict.fromkeys(titles)))
    #             return (
    #                 value,
    #                 norm_last,
    #                 norm_first,
    #                 result.get("electorate2") or result.get("electorate1"),
    #                 self._normalise.state(result.get("state1")),
    #                 titles,
    #             )
    #
    #     norm_name, norm_titles = self._norm_name(value)
    #     if not value or not norm_name:
    #         return value, None, None, None, None, None
    #     raise ValueError(value)
    #
    # def norm_text(self, value: str):
    #     value = value.strip() if value else ""
    #     replacements = {
    #         "–": "-",
    #         "—": "-",
    #         "\xa0": " ",  # \xa0 is NBSP
    #         "  ": " ",
    #     }
    #     for find, replace in replacements.items():
    #         value = value.replace(find, replace)
    #     return value
    #
    # def norm_name(self, value: str):
    #     titles = []
    #
    #     replacements = [
    #         "(PDF",
    #         "( PDF",
    #         "(",
    #         ")",
    #         "Vol 1 -",
    #         "Volume 1 -",
    #         "Vol 1 ",
    #         "Vol 2 -",
    #         "Volume 2 -",
    #         "Vol 2 ",
    #     ]
    #     for replace in replacements:
    #         value = value.replace(replace, "")
    #
    #     return value.strip(), titles
