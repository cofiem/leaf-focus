import json
from logging import Logger
from pathlib import Path

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

        # get the hash of the source file
        path = details.get("path")
        file_hash = self._identify.file_hash(path)

        # get the hash and hash type to the details
        identify = {
            "pdf_file": str(path),
            "hash_type": self._identify.file_hash_type,
            "file_hash": file_hash,
        }

        # get the path to write the identify file
        output_file = self._location.identify_file(base_dir, file_hash)

        # write the identify file as json
        with open(output_file, "wt") as f:
            json.dump(identify, f)

        return output_file
