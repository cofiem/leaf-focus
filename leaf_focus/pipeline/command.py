import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import click

from leaf_focus.pipeline.prefect_flow.construct import Construct


def validate_threshold(ctx, param, value):
    if 0 <= value <= 255:
        return value
    raise click.BadParameter(
        "must be greater than or equal to 0 and less than or equal to 255"
    )


@click.group()
def pipeline():
    """Run or view the pipeline of tasks."""
    pass


@pipeline.command(name="full")
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
def pipeline_full(
    feed_dir: Path,
    base_dir: Path,
    pdf_info_exe: Path,
    pdf_text_exe: Path,
    pdf_image_exe: Path,
    threshold: int,
):
    """Run the full pipeline."""
    click.secho("Starting pipeline run.", bold=True)

    logger = logging.getLogger()
    log_data = {
        "feed_dir": str(feed_dir),
        "base_dir": str(base_dir),
        "pdf_info_exe": str(pdf_info_exe),
        "pdf_text_exe": str(pdf_text_exe),
        "pdf_image_exe": str(pdf_image_exe),
        "threshold": str(threshold),
    }
    log_msg = ", ".join([f"{k}={v}" for k, v in log_data.items()])
    logger.info(f"Running pipeline using {log_msg}.")

    c = Construct()
    c.run_full(
        feed_dir=feed_dir,
        base_dir=base_dir,
        threshold=threshold,
        pdf_info_exe=pdf_info_exe,
        pdf_text_exe=pdf_text_exe,
        pdf_image_exe=pdf_image_exe,
    )
    click.secho("Finished pipeline run.", bold=True)


@pipeline.command(name="pdf")
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
def pipeline_pdf(
    feed_dir: Path,
    base_dir: Path,
    pdf_info_exe: Path,
    pdf_text_exe: Path,
    pdf_image_exe: Path,
):
    """Run the pdf pipeline."""
    click.secho("Starting pdf pipeline run.", bold=True)

    logger = logging.getLogger()

    log_data = {
        "feed_dir": str(feed_dir),
        "base_dir": str(base_dir),
        "pdf_info_exe": str(pdf_info_exe),
        "pdf_text_exe": str(pdf_text_exe),
        "pdf_image_exe": str(pdf_image_exe),
    }
    log_msg = ", ".join([f"{k}={v}" for k, v in log_data.items()])
    logger.info(f"Running pipeline using {log_msg}.")

    c = Construct()
    c.run_pdf(
        feed_dir=feed_dir,
        base_dir=base_dir,
        pdf_info_exe=pdf_info_exe,
        pdf_text_exe=pdf_text_exe,
        pdf_image_exe=pdf_image_exe,
    )
    click.secho("Finished pdf pipeline run.", bold=True)


@pipeline.command(name="ocr")
@click.option(
    "-b",
    "--base-dir",
    "base_dir",
    required=True,
    type=Path,
    help="Path to the base directory.",
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
def pipeline_ocr(base_dir: Path, threshold: int):
    """Run the ocr pipeline."""
    click.secho("Starting ocr pipeline run.", bold=True)

    logger = logging.getLogger()
    log_data = {"base_dir": str(base_dir), "threshold": str(threshold)}
    log_msg = ", ".join([f"{k}={v}" for k, v in log_data.items()])
    logger.info(f"Running pipeline using {log_msg}.")

    c = Construct()
    c.run_ocr(base_dir=base_dir, threshold=threshold)
    click.secho("Finished ocr pipeline run.", bold=True)


@pipeline.command(name="visualise")
@click.option(
    "-v",
    "--visual-file",
    "visualise_path",
    required=True,
    type=Path,
    help="Path to the output visualise image file.",
)
def pipeline_visualise(visualise_path: Path):
    """Visualise the full pipeline."""
    click.secho("Starting pipeline visualise.", bold=True)
    c = Construct()
    with TemporaryDirectory() as d:
        temp_file = Path(d, "placeholder-file")
        temp_file.touch()
        c.visualise(
            base_dir=d,
            threshold=0,
            pdf_info_exe=temp_file,
            pdf_text_exe=temp_file,
            pdf_image_exe=temp_file,
            visualise_path=visualise_path,
        )
    click.secho("Finished pipeline visualise.", bold=True)
