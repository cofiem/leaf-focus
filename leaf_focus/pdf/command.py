import logging
from pathlib import Path

import click


@click.group()
def pdf():
    """Extract information from pdf files."""
    pass


@pdf.command(name="identify")
@click.option(
    "-i",
    "--input",
    "input_file",
    required=True,
    type=Path,
    help="Path to the input pdf file.",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    required=True,
    type=Path,
    help="Path to the output identify json file.",
)
def pdf_identify(input_file: Path, output_file: Path):
    """Identify a pdf for use in other operations."""
    from leaf_focus.pdf.identify import Component

    click.secho("Starting pdf identify.", bold=True)

    logger = logging.getLogger()
    c = Component(logger)
    file_hash = c.file_hash(input_file)
    c.create(input_file, file_hash, output_file)

    click.secho("Finished pdf identify.", bold=True)


@pdf.command(name="info")
@click.option(
    "-e",
    "--exe",
    "exe_file",
    required=True,
    type=Path,
    help="Path to the xpdf pdfinfo executable.",
)
@click.option(
    "-i",
    "--input",
    "input_file",
    required=True,
    type=Path,
    help="Path to the input pdf file.",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    required=True,
    type=Path,
    help="Path prefix for the output info json file.",
)
def pdf_info(exe_file: Path, input_file: Path, output_file: Path):
    """Extract the pdf metadata."""
    from leaf_focus.pdf.info.component import Component

    click.secho("Starting pdf images.", bold=True)

    logger = logging.getLogger()
    c = Component(logger, exe_file)
    c.create(input_file, output_file)

    click.secho("Finished pdf info.", bold=True)


@pdf.command(name="text")
@click.option(
    "-e",
    "--exe",
    "exe_file",
    required=True,
    type=Path,
    help="Path to the xpdf pdftotext executable.",
)
@click.option(
    "-i",
    "--input",
    "input_file",
    required=True,
    type=Path,
    help="Path to the input pdf file.",
)
@click.option(
    "-o",
    "--output",
    "output_prefix",
    required=True,
    type=Path,
    help="Path to the output text file.",
)
def pdf_text(exe_file: Path, input_file: Path, output_prefix: Path):
    """Extract embedded text from a pdf."""
    from leaf_focus.pdf.text.component import Component

    click.secho("Starting pdf text.", bold=True)

    logger = logging.getLogger()
    c = Component(logger, exe_file)
    c.create(input_file, output_prefix)

    click.secho("Finished pdf text.", bold=True)


@pdf.command(name="images")
@click.option(
    "-e",
    "--exe",
    "exe_file",
    required=True,
    type=Path,
    help="Path to the xpdf pdftopng executable.",
)
@click.option(
    "-i",
    "--input",
    "input_file",
    required=True,
    type=Path,
    help="Path to the input pdf file.",
)
@click.option(
    "-o",
    "--output",
    "output_prefix",
    required=True,
    type=Path,
    help="Path prefix for the output files.",
)
def pdf_images(exe_file: Path, input_file: Path, output_prefix: Path):
    """Create images from pages of a pdf."""

    from leaf_focus.pdf.images.component import Component

    click.secho("Starting pdf images.", bold=True)

    logger = logging.getLogger()
    c = Component(logger, exe_file)
    result = c.create(input_file, output_prefix)

    click.secho(
        f"There are {len(result)} images created from the pdf pages.", fg="bright_blue"
    )
    click.secho("Finished pdf images.", bold=True)
