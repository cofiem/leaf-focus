import click

from leaf_focus.download.command import download
from leaf_focus.ocr.command import ocr
from leaf_focus.pdf.command import pdf
from leaf_focus.pipeline.command import pipeline_visualise
from leaf_focus.report.command import report
from leaf_focus.support.log_config import configure_leaf_focus_logging


@click.group()
@click.version_option()
def cli():
    """Extract structured text from pdf files."""
    pass


cli.add_command(download)
cli.add_command(pdf)
cli.add_command(ocr)
cli.add_command(pipeline_visualise)
cli.add_command(report)


if __name__ == "__main__":

    # only configure the logging when this script is run as main
    configure_leaf_focus_logging()
    cli()
