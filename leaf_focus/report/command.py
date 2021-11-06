import logging
from importlib import resources
from pathlib import Path

import click

from leaf_focus.report.item.document import Document
from leaf_focus.report.item.correction import Correction
from leaf_focus.report.item.known_text import KnownText
from leaf_focus.report.item.line_parser import LineParser
from leaf_focus.report.item.report_entry import ReportEntry
from leaf_focus.report.processing.normalise import Normalise
from leaf_focus.report.processing.parse import Parse
from leaf_focus.report.item.section import Section
from leaf_focus.report.item.skipped_line import SkippedLine
from leaf_focus.report.item.skipped_page import SkippedPage
from leaf_focus.support.config import Config


@click.command()
@click.option(
    "-c",
    "--config-file",
    "config_file",
    type=Path,
    help="Path to the config file.",
)
def report(config_file: Path):
    """Create a report."""
    if not config_file:
        raise click.UsageError("Must provide config file.")

    click.secho("Starting report.", bold=True)

    package = "leaf_focus.resources"

    # load line parsers
    names = [
        "parse-alterations.yml",
        "parse-metadata.yml",
        "parse-sections-line.yml",
        "parse-sections-table.yml",
    ]
    parsers = []
    for name in names:
        with resources.path(package, name) as p:
            parsers.extend(LineParser.load(p))

    # load sections
    with resources.path(package, "sections.yml") as p:
        sections = list(Section.load(p))

    # load normalisations
    with resources.path(package, "corrections.yml") as p:
        corrections = list(Correction.load(p))
    with resources.path(package, "known-text.yml") as p:
        known_text = list(KnownText.load(p))
    normalise = Normalise(corrections=corrections, known_text=known_text)

    # create parser
    logger = logging.getLogger()
    config = Config.load(config_file)
    parse = Parse(logger, config, parsers, sections, normalise)
    docs = Document.load(config.processing_dir, config.feed_dir)

    # run parser
    items = (item for item in parse.documents(docs))

    # create report
    ReportEntry.save(config.report_dir / "report.csv", items)
    SkippedLine.save(config.report_dir / "skipped-lines.csv", parse.skipped_lines)
    SkippedPage.save(config.report_dir / "skipped-pages.csv", parse.skipped_pages)

    click.secho("Finished report.", bold=True)
