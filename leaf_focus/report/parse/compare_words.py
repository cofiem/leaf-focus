class CompareWords:
    def __init__(self, value: list[str], compare: list[list[str]]):
        self.value = value
        self.compare = compare
        self._threshold = 0.4
        self._matched = self._do_match(value, compare, self._threshold)
        self._selected = self._do_select(self._matched)
        self._str = self._do_str(self._selected)

    @property
    def result(self):
        return self._selected

    @property
    def percentage(self):
        if not self._selected:
            return None
        line_percent = self._selected.get("line_percent")
        value_percent = self._selected.get("value_percent")
        return min([line_percent, value_percent])

    def __str__(self):
        return self._str

    def _do_match(self, value: list[str], compare: list[list[str]], threshold: float):
        found = []
        for compare_line_index, compare_line in enumerate(compare):
            line_found = []
            recent_found_index = 0
            line_count = 0
            line_match = 0
            for compare_item_index, compare_item in enumerate(compare_line):
                line_count += 1
                try:
                    word_index = value.index(compare_item, compare_item_index)
                    if word_index < recent_found_index:
                        continue
                    recent_found_index = word_index
                    line_match += 1
                    line_found.append(
                        {
                            "word": compare_item,
                            "found_index": word_index,
                            "compare_item": compare_item_index,
                        }
                    )
                except ValueError:
                    pass

            if line_match < 1:
                continue
            line_percent = line_match / line_count
            if line_percent < threshold:
                continue
            value_percent = line_match / len(value)
            if value_percent < threshold:
                continue
            found.append(
                {
                    "line_count": line_count,
                    "line_index": compare_line_index,
                    "line_match": line_match,
                    "line_percent": line_percent,
                    "value_percent": value_percent,
                    "line_found": line_found,
                }
            )

        return found

    def _do_str(self, item: dict):
        if not item:
            return "(no matches)"
        line = []
        line_count = item.get("line_count")
        line_match = item.get("line_match")
        line_percent = item.get("line_percent")
        value_percent = item.get("value_percent")

        for found in item.get("line_found"):
            line_len = len(line)
            word = found["word"]
            found_index = found["found_index"]
            if found_index > line_len:
                line.extend(["_"] * (found_index - line_len))
            line.append(word)

        line_len = len(line)
        if line_len < line_count:
            line.extend(["_"] * (line_count - line_len))

        return f'"{" ".join(line)}" (matched {line_match} - {line_percent:.0%} | {value_percent:.0%})'

    def _do_select(self, matched):
        if not matched:
            return None
        ordered = sorted(
            matched,
            reverse=True,
            key=lambda x: (
                x["line_count"],
                x["line_match"],
                x["line_percent"],
            ),
        )
        return ordered[0]
