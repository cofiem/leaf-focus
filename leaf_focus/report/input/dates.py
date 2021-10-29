from datetime import datetime
from pathlib import Path


class Dates:
    def parse(self, value: str):
        if not value:
            return None

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

        if not value:
            return None

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
            "%d%b %Y",
            # examples: '28 March2019'
            "%d %B%Y",
            # examples: '28 Mar2019'
            "%d %b%Y",
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
                formatted = parsed.date().isoformat()
                return formatted
            except ValueError:
                continue

        raise ValueError(value)

    def downloaded(self, path: Path):
        if not path.exists():
            return None
        modified_timestamp = path.stat().st_mtime
        modified_datetime = datetime.fromtimestamp(modified_timestamp)
        formatted = modified_datetime.date().isoformat()
        return formatted
