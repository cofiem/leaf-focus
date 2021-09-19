from pathlib import Path

import click


@click.group()
def ocr():
    """Run Optical Character Recogition."""
    pass


@ocr.command(name="prepare")
def ocr_prepare(base_dir: Path):
    """Prepare an image for OCR."""
    click.echo("ocr prepare")


@ocr.command(name="recognise")
def ocr_recognise(base_dir: Path):
    """Prepare an image for OCR."""
    click.echo("ocr prepare")
