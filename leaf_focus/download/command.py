import logging
from pathlib import Path
import click


@click.command()
@click.option(
    "-f",
    "--feed-dir",
    "feed_dir",
    required=True,
    type=Path,
    help="Path to the feed output directory.",
)
@click.option(
    "-c",
    "--cache-dir",
    "cache_dir",
    required=True,
    type=Path,
    help="Path to the cache directory.",
)
@click.option(
    "-d",
    "--domain",
    "allowed_domains",
    required=True,
    multiple=True,
    type=str,
    help="An allowed domain. May be specified multiple times.",
)
@click.option(
    "-u",
    "--url",
    "urls",
    required=True,
    multiple=True,
    type=str,
    help="A starting url. May be specified multiple times.",
)
def download(
    feed_dir: Path, cache_dir: Path, allowed_domains: list[str], urls: list[str]
):
    """Find and download pdfs."""
    from leaf_focus.download.crawl.component import Component

    click.secho("Starting download.", bold=True)

    logger = logging.getLogger()
    c = Component(logger, feed_dir, cache_dir)
    urls = [{"category": "default", "comment": None, "url": i} for i in urls if i]
    c.run(allowed_domains, urls)

    click.secho("Finished download.", bold=True)
