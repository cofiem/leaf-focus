import logging
from importlib import resources
from pathlib import Path

import click

from leaf_focus.report.input.document import Document
from leaf_focus.report.output.correction import Correction
from leaf_focus.report.output.item import Item as ReportItem
from leaf_focus.report.output.definition import Definition
from leaf_focus.report.output.line_parser import LineParser
from leaf_focus.report.output.parse import Parse
from leaf_focus.report.output.section import Section
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

    logger = logging.getLogger()
    config = Config.load(config_file)

    docs = Document.load(config.processing_dir, config.feed_dir)

    package = "leaf_focus.resources"
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

    with resources.path(package, "sections.yml") as p:
        sections = list(Section.load(p))

    with resources.path(package, "corrections.yml") as p:
        corrections = list(Correction.load(p))

    parse = Parse(logger, parsers, sections, corrections, config.urls)
    items = (item for item in parse.documents(docs))
    ReportItem.save(config.report_dir / "report.csv", items)

    click.secho("Finished report.", bold=True)
