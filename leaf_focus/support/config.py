from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Config:

    feed_dir: Path
    cache_dir: Path
    processing_dir: Path
    report_dir: Path

    pdf_info: Path
    pdf_text: Path
    pdf_image: Path

    prepare_image_threshold: int

    allowed_domains: list[str]

    urls: list[dict]

    @classmethod
    def load(cls, path: Path):
        """Load config from a file."""
        with open(path, "rt", encoding="utf8") as f:
            data = yaml.safe_load(f)
            directories = data["directories"]
            xpdf = data["xpdf"]
            settings = data["settings"]
            return Config(
                feed_dir=Path(directories["feed"]),
                cache_dir=Path(directories["cache"]),
                processing_dir=Path(directories["processing"]),
                report_dir=Path(directories["report"]),
                pdf_info=Path(xpdf["info"]),
                pdf_text=Path(xpdf["text"]),
                pdf_image=Path(xpdf["image"]),
                prepare_image_threshold=settings["imagethreshold"],
                allowed_domains=data["allowed_domains"],
                urls=data["urls"],
            )
