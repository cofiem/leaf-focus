import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ImageItem:

    path: Path
    page: int
    threshold: Optional[int]
    variety: Optional[str]

    _pattern = re.compile(
        rf"^pdf-page-(?P<page>\d{{6}})(-(?P<variety>[^-]+))?(-th-(?P<threshold>[^-]+))?$"
    )

    @classmethod
    def load(cls, directory: Path):
        for path in directory.glob("*.png"):
            try:
                yield cls.read(path)
            except ValueError:
                pass

    @classmethod
    def read(cls, path: Path):
        match = cls._pattern.match(path.stem)
        if not match:
            raise ValueError(f"File is not a recognised image '{path}'.")

        matches = match.groupdict()
        page = int(matches.get("page"), 10)
        variety = matches.get("variety")
        threshold = matches.get("threshold")

        return ImageItem(path=path, page=page, threshold=threshold, variety=variety)

    @classmethod
    def build(
        cls,
        page: int,
        variety: Optional[str] = None,
        threshold: Optional[int] = None,
        suffix: str = ".png",
    ) -> str:
        parts = [
            "pdf-page",
            f"{page:06}",
            variety,
            "th" if threshold is not None else "",
            f"{threshold:03}" if threshold is not None else "",
        ]
        stem = "-".join([i for i in parts if i])
        name = f"{stem}{suffix}"
        return name

    @property
    def stem(self) -> str:
        return Path(self.build(self.page, self.variety, self.threshold)).stem
