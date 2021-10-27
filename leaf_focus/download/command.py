import json
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
    "-g",
    "--config-file",
    "config_files",
    multiple=True,
    type=Path,
    help="Path to a config file containing domains and urls. "
    "May be specified multiple times.",
)
@click.option(
    "-d",
    "--domain",
    "allowed_domains",
    multiple=True,
    type=str,
    help="An allowed domain. May be specified multiple times.",
)
@click.option(
    "-u",
    "--url",
    "urls",
    multiple=True,
    type=str,
    help="A starting url. May be specified multiple times.",
)
def download(
    feed_dir: Path,
    cache_dir: Path,
    config_files: list[Path] = None,
    allowed_domains: list[str] = None,
    urls: list[str] = None,
):
    """Find and download pdfs."""
    from leaf_focus.download.crawl.component import Component

    click.secho("Starting download.", bold=True)

    logger = logging.getLogger()
    c = Component(logger, feed_dir, cache_dir)

    if not config_files and not allowed_domains and not urls:
        raise click.UsageError(
            "Must provide at least one config file, "
            "or both allowed domains and urls. "
            "Can also provide all three."
        )

    combined_urls = []
    combined_allowed_domains = []

    if urls:
        combined_urls.extend(
            [{"category": "default", "comment": None, "url": i} for i in urls if i]
        )

    if allowed_domains:
        combined_allowed_domains.extend(allowed_domains)

    if config_files:
        for config_file in config_files:
            with open(config_file, "rt") as f:
                data = json.load(f)
                combined_allowed_domains.extend(data.get("allowed_domains", []))
                combined_urls.extend(data.get("urls", []))

    c.run(combined_allowed_domains, combined_urls)

    click.secho("Finished download.", bold=True)
