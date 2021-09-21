import logging
from pathlib import Path

import click


def validate_threshold(ctx, param, value):
    if 0 <= value <= 255:
        return value
    raise click.BadParameter(
        "must be greater than or equal to 0 and less than or equal to 255"
    )


@click.group()
def ocr():
    """Run Optical Character Recogition."""
    pass


@ocr.command(name="prepare")
@click.option(
    "-i",
    "--input",
    "input_file",
    required=True,
    type=Path,
    help="Path to the input image file.",
)
@click.option(
    "-o",
    "--output",
    "output_file",
    required=True,
    type=Path,
    help="Path to the output prepared image file.",
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
def ocr_prepare(input_file: Path, output_file: Path, threshold: int):
    """Prepare an image for OCR."""

    from leaf_focus.ocr.prepare.component import Component

    click.secho("Starting ocr prepare.", bold=True)

    logger = logging.getLogger()
    c = Component(logger)
    c.threshold(input_file, output_file, threshold)

    click.secho("Finished ocr prepare.", bold=True)


@ocr.command(name="recognise")
@click.option(
    "-i",
    "--input",
    "input_file",
    required=True,
    type=Path,
    help="Path to the input image file.",
)
@click.option(
    "-a",
    "--annotations",
    "annotations_file",
    required=True,
    type=Path,
    help="Path to the output annotations file.",
)
@click.option(
    "-p",
    "--predictions",
    "predictions_file",
    required=True,
    type=Path,
    help="Path to the output predictions file.",
)
def ocr_recognise(image_file: Path, annotation_file: Path, predictions_file: Path):
    """Recognise the text in an image."""

    from leaf_focus.ocr.recognise.component import Component

    click.secho("Starting ocr recognise.", bold=True)

    logger = logging.getLogger()
    c = Component(logger)
    c.recognise_text(image_file, annotation_file, predictions_file)

    click.secho("Finished ocr recognise.", bold=True)
