from logging import Logger
from pathlib import Path

from leaf_focus.report.report_service import ReportService


class Report:

    command = "report"
    description = "Recognise text from each line of each pdf page."

    def build(self, sub_parser) -> None:
        """Build the command line."""
        pass

    def run(self, parsed_args, logger: Logger):
        """Run using the parsed args."""
        base_dir = parsed_args.base_dir  # type: Path
        report = ReportService(self._logger)
        report.start(base_dir)
