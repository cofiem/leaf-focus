from logging import Logger
from pathlib import Path


class Identify:
    def __init__(self, logger: Logger):
        self._logger = logger

    @property
    def file_hash_type(self):
        return "SHA256"

    def file_hash(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Path does not exist '{path}'.")

        import hashlib

        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
