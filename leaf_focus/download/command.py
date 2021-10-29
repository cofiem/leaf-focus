import logging
from pathlib import Path
import click

from leaf_focus.support.config import Config


@click.command()
@click.option(
    "-c",
    "--config-file",
    "config_file",
    type=Path,
    help="Path to the config file.",
)
def download(config_file: Path):
    """Find and download pdfs."""
    from leaf_focus.download.crawl.component import Component

    if not config_file:
        raise click.UsageError("Must provide config file.")

    click.secho("Starting download.", bold=True)

    config = Config.load(config_file)

    logger = logging.getLogger()
    c = Component(logger, config.feed_dir, config.cache_dir)

    c.run(config.allowed_domains, config.urls)

    click.secho("Finished download.", bold=True)
