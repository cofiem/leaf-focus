import logging
from pathlib import Path

import click

from leaf_focus.pipeline.prefect_flow.construct import Construct
from leaf_focus.support.config import Config


@click.group()
def pdf():
    """Extract information and text from pdf files."""
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
    from leaf_focus.pdf.identify.component import Component

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


@pdf.command(name="all")
@click.option(
    "-c",
    "--config-file",
    "config_file",
    type=Path,
    help="Path to the config file.",
)
def pdf_all(config_file: Path):
    """Run all the pdf steps using multiple pdf files."""

    if not config_file:
        raise click.UsageError("Must provide config file.")

    click.secho("Starting pdf all.", bold=True)

    config = Config.load(config_file)
    logger = logging.getLogger()

    log_data = {
        "feed_dir": str(config.feed_dir),
        "base_dir": str(config.processing_dir),
        "pdf_info_exe": str(config.pdf_info_exe),
        "pdf_text_exe": str(config.pdf_text_exe),
        "pdf_image_exe": str(config.pdf_image_exe),
    }
    log_msg = ", ".join([f"{k}={v}" for k, v in log_data.items()])
    logger.info(f"Running all using {log_msg}.")

    c = Construct()
    c.run_pdf(
        feed_dir=config.feed_dir,
        base_dir=config.processing_dir,
        pdf_info_exe=config.pdf_info_exe,
        pdf_text_exe=config.pdf_text_exe,
        pdf_image_exe=config.pdf_image_exe,
    )
    click.secho("Finished pdf all.", bold=True)
