from pathlib import Path

from scrapy.utils.serialize import ScrapyJSONEncoder, ScrapyJSONDecoder


class LeafFocusJsonEncoder(ScrapyJSONEncoder):
    def default(self, o):
        if isinstance(o, Path):
            return str(o)
        else:
            return super().default(o)


class LeafFocusJsonDecoder(ScrapyJSONDecoder):
    pass
