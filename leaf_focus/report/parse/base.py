import re
from typing import Optional

from download.crawl.item import Item
from report.gather.content_item import ContentItem
from report.gather.metadata_item import MetadataItem
from report.gather.normalise import Normalise


class Base:
    def __init__(self):
        self._re_line_norm = re.compile(r"[^a-zA-Z0-9 ]")
        self._re_collapse_spaces = re.compile(r"\s+")
        self._normalise = Normalise()

    def run(
        self,
        text_info: MetadataItem,
        text_extracted: list[str],
        text_found: list[Item],
        page_number: int,
        shared_data: dict,
    ) -> Optional[list[ContentItem]]:
        raise NotImplementedError()

    def _normalise_str(self, line: str):
        line_norm = line
        line_norm = self._re_line_norm.sub("", line_norm)
        line_norm = self._re_collapse_spaces.sub(" ", line_norm)
        line_norm = line_norm.strip()
        return line_norm

    def _line_words(self, line_norm: str):
        line_split = line_norm.split(" ")
        line_words = [w.lower() for w in line_split]
        return line_words
