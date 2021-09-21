from pathlib import Path

import click

from leaf_focus.pipeline.prefect_flow.construct import Construct


def validate_threshold(ctx, param, value):
    if 0 <= value <= 255:
        return value
    raise click.BadParameter(
        "must be greater than or equal to 0 and less than or equal to 255"
    )


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
    "-b",
    "--base-dir",
    "base_dir",
    required=True,
    type=Path,
    help="Path to the base directory.",
)
@click.option(
    "--info-exe",
    "pdf_info_exe",
    required=True,
    type=Path,
    help="Path to the xpdf pdfinfo executable.",
)
@click.option(
    "--text-exe",
    "pdf_text_exe",
    required=True,
    type=Path,
    help="Path to the xpdf pdftotext executable.",
)
@click.option(
    "--image-exe",
    "pdf_image_exe",
    required=True,
    type=Path,
    help="Path to the xpdf pdftopng executable.",
)
@click.option(
    "-t",
    "--threshold",
    "threshold",
    type=int,
    default=190,
    callback=validate_threshold,
    help="The threshold to use for the prepared image file. Default is 190.",
)
def pipeline(
    feed_dir: Path,
    base_dir: Path,
    pdf_info_exe: Path,
    pdf_text_exe: Path,
    pdf_image_exe: Path,
    threshold: int,
):
    """Run a pipeline of tasks."""
    c = Construct()
    c.run(
        feed_dir=feed_dir,
        base_dir=base_dir,
        threshold=threshold,
        pdf_info_exe=pdf_info_exe,
        pdf_text_exe=pdf_text_exe,
        pdf_image_exe=pdf_image_exe,
    )
