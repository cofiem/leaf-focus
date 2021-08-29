from logging import Logger
from pathlib import Path


class Pipeline:

    command = "pipeline"
    description = "Run the pdf processing pipeline."

    def build(self, sub_parser) -> None:
        """Build the command line."""
        pass

    def run(self, parsed_args, logger: Logger):
        """Run using the parsed args."""
        config_file = parsed_args.config_file  # type: Path

        # find the scrapy output items and create background tasks for each item
