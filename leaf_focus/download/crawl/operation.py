import importlib.resources
import json
from logging import Logger
from pathlib import Path

from leaf_focus.download.crawl.component import Component
from leaf_focus.support.location import Location


class Operation:
    """An independent operation that runs the download."""

    def __init__(self, logger: Logger, feed_dir: Path, cache_dir: Path):
        self._logger = logger
        self._location = Location(logger)
        self._component = Component(logger, feed_dir, cache_dir)

    def run(self, name: str):
        """Run the operation."""
        config = self.load_config(name)

        dl = config.get("download", {})
        allowed_domains = dl.get("allowed_domains", [])
        start_urls = dl.get("start_urls", [])

        self._component.run(allowed_domains, start_urls)

    def load_config(self, name: str) -> dict:
        """Load a config file."""
        package = "leaf_focus.resources"
        name = str(Path(name).with_suffix(".json"))
        with importlib.resources.open_text(package, name) as f:
            return json.load(f)
