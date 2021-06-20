import logging

from leaf_focus.text.found_text import FoundText


class TextService:
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def order_text_lines(self, items: list[FoundText]):
        """Put items into lines of text (top -> bottom, left -> right)."""
        self._logger.info(f"Arranging text into lines.")

        lines = []
        current_line = []
        for item in items:
            if not item.is_top_horizontal:
                # exclude items that are too sloped
                continue

            if len(current_line) < 1:
                current_line.append(item)

            elif any([item.is_same_line(i) for i in current_line]):
                current_line.append(item)

            elif len(current_line) > 0:
                # store current line
                current_line = sorted(current_line, key=lambda x: x.top_left)
                lines.append(current_line)

                # create new line
                current_line = [item]

        if len(current_line) > 0:
            lines.append(current_line)

        for line_index, line in enumerate(lines):
            for item_index, item in enumerate(line):
                item.line_number = line_index + 1
                item.line_order = item_index + 1

        return lines
