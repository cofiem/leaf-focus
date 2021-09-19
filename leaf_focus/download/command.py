from pathlib import Path

import click


@click.command()
def download(base_dir: Path):
    """Find and download pdfs."""
    click.echo("download")
