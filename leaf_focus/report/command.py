from pathlib import Path

import click

from leaf_focus.report.input.document import Document
from leaf_focus.report.output.item import Item as ReportItem
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

    config = Config.load(config_file)
    docs = Document.load(config.processing_dir, config.feed_dir)
    items = (item for doc in docs for item in doc.parse())
    ReportItem.save(config.report_dir / "report.csv", items)

    click.secho("Finished report.", bold=True)
