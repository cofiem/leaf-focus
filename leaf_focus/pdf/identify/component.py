from logging import Logger
from pathlib import Path


from leaf_focus.pdf.identify.item import Item


class Component:
    """Create the pdf identify file."""

    def __init__(self, logger: Logger):
        self._logger = logger

    @property
    def file_hash_type(self):
        return "SHA256"

    def file_hash(self, path: Path):
        """Calculate the hash of a file."""

        if not path.exists():
            raise FileNotFoundError(f"Path does not exist '{path}'.")

        import hashlib

        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()

    def create(self, pdf_path: Path, file_hash: str, identify_path: Path):
        """Create a file that identifies a pdf."""

        if not pdf_path:
            raise ValueError("Must supply pdf file.")
        if not identify_path:
            raise ValueError("Must supply identify file.")
        if not pdf_path.exists():
            raise FileNotFoundError(f"Pdf file does not exist '{pdf_path}'.")

        # get the hash of the source file
        hash_type = self.file_hash_type

        # write the identify file as json
        item = Item(pdf_file=pdf_path, hash_type=hash_type, file_hash=file_hash)
        item.write(identify_path)
