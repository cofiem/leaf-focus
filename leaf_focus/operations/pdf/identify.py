import json
from logging import Logger
from pathlib import Path

from leaf_focus.components.serialise import LeafFocusJsonEncoder
from leaf_focus.components.store.location import Location
from leaf_focus.support.config import Config
from leaf_focus.components.store.identify import Identify as StoreIdentify


class Identify:
    def __init__(self, logger: Logger, config: Config):
        self._logger = logger
        self._config = config

        self._location = Location(logger)
        self._identify = StoreIdentify(logger)

    def run(self, details_file: Path, base_dir: Path):
        """Create the pdf identify file containing file hash details."""

        # load the details file
        with open(details_file, "rt") as f:
            details = json.load(f)

        # paths
        pdf_path = Path(details.get("path"))
        output_file = self._location.identify_file(pdf_path)
        self._location.create_directory(output_file.parent)

        # get the hash and hash type to the details
        identify = {}

        # see if the identify file already exists
        if output_file.exists():
            with open(output_file, "rt") as f:
                identify = json.load(f)

        if (
            not identify.get("pdf_file")
            or not identify.get("hash_type")
            or not identify.get("file_hash")
        ):
            # get the hash of the source file
            file_hash = self._identify.file_hash(pdf_path)

            identify = {
                "pdf_file": str(pdf_path),
                "hash_type": self._identify.file_hash_type,
                "file_hash": file_hash,
            }

            # write the identify file as json
            with open(output_file, "wt") as f:
                json.dump(identify, f, indent=2, cls=LeafFocusJsonEncoder)

        return output_file
