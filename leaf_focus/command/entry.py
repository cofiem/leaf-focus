import logging
from argparse import ArgumentParser
from pathlib import Path

from leaf_focus.command.download import Download
from leaf_focus.command.pipeline import Pipeline
from leaf_focus.command.report import Report


class Entry:
    def __init__(self):
        self._download = Download()
        self._pipeline = Pipeline()
        self._report = Report()

    def build(self):
        parser = ArgumentParser(
            description="Extract text from pdf files.",
        )
        parser.add_argument(
            "--config-file",
            type=Path,
            help="Path to the config file.",
        )
        subparsers = parser.add_subparsers(
            dest="sub_parser_name",
            help="Available commands.",
        )

        # create the parser for the download command
        sub_parser_download = subparsers.add_parser(
            self._download.command,
            help=self._download.description,
        )
        self._download.build(sub_parser_download)

        # create the parser for the pipeline command
        sub_parser_pipeline = subparsers.add_parser(
            self._pipeline.command,
            help=self._pipeline.description,
        )
        self._pipeline.build(sub_parser_pipeline)

        # create the parser for the "report" command
        sub_parser_report = subparsers.add_parser(
            self._report.command,
            help=self._report.description,
        )
        self._report.build(sub_parser_report)

        return parser

    def run(self, parser):
        parsed_args = parser.parse_args()
        if not parsed_args.sub_parser_name:
            parser.print_help()
            return

        name = parsed_args.sub_parser_name

        cmd_download = self._download.command
        cmd_pipeline = self._pipeline.command
        cmd_report = self._report.command

        # scrapy has an internal logger
        if name != cmd_download:
            self._create_logger()
            self._logger.info("Starting leaf focus...")

        if name == cmd_download:
            self._download.run(parsed_args)
        elif name == cmd_pipeline:
            self._pipeline.run(parsed_args, self._logger)
        elif name == cmd_report:
            self._report.run(parsed_args, self._logger)
        else:
            raise ValueError(f"Unrecognised activity '{name}'.")

        if name != cmd_download:
            self._logger.info("Finished leaf focus.")

    def _create_logger(self):
        logging.basicConfig(
            format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s",
            level=logging.INFO,
        )
        self._logger = logging.getLogger("leaf-focus")
