import logging
from pathlib import Path

import mmh3

logger = logging.getLogger(__name__)


class FileCache:
    def __init__(self, base_dir: Path):
        self._base_dir = base_dir

    def path(self, key: str, suffix: str) -> Path:
        hashed_key = hex(mmh3.hash(key, signed=False))
        path = self._base_dir / hashed_key[0:2] / hashed_key
        path = path.with_suffix(suffix)
        path.parent.mkdir(exist_ok=True, parents=True)
        return path
