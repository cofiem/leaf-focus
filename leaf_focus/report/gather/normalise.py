import re


class Normalise:
    def state(self, value: str):
        if not value:
            return None
        alpha = re.compile("[^a-zA-Z ]")
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
        result = known.get(value, None)
        if result is None:
            return value
        return result
