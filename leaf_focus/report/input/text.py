import re
from collections import OrderedDict


class Text:

    _collapse_spaces_re = re.compile(r"\s+")

    def parse_name(self, value: str):
        value = self.norm_text(value)

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
                fr"^(?P<last1>[^,]+),? (?P<title1>{member_titles}) "
                + rf"(?P<first1>[^,]+), (({member_prefixes}) )((?P<electorate1>.+), "
                + r"(?P<state1>.+)|(?P<electorate2>[^,]+))?$"
            ),
            # senate
            re.compile(
                fr"^(?P<last1>.+[^,]+), (?P<title1>{senator_titles}) "
                + r"(?:(?P<first1>.+)( - (Senator for) (?P<state1>.+))|(?P<first2>.+))$"
            ),
        ]
        for pattern in patterns:
            match = pattern.fullmatch(value)
            if match:
                result = match.groupdict()
                norm_last, titles_last = self._norm_name(result.get("last1"))
                norm_first, titles_first = self._norm_name(
                    result.get("first1") or result.get("first2")
                )
                titles = (
                    result.get("title1", "").split(" ") + titles_last + titles_first
                )
                titles = " ".join(list(OrderedDict.fromkeys(titles)))
                return (
                    value,
                    norm_last,
                    norm_first,
                    result.get("electorate2") or result.get("electorate1"),
                    self._normalise.state(result.get("state1")),
                    titles,
                )

        norm_name, norm_titles = self._norm_name(value)
        if not value or not norm_name:
            return value, None, None, None, None, None
        raise ValueError(value)

    def norm_text(self, value: str):
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

    def norm_name(self, value: str):
        titles = []
        if value.endswith(", AO"):
            value = value[0:-4]
            titles.append("AO")
        if value.endswith(" AO"):
            value = value[0:-3]
            titles.append("AO")

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

        return value.strip(), titles

    @classmethod
    def collapse_spaces(cls, value: str) -> str:
        return cls._collapse_spaces_re.sub(" ", value)
