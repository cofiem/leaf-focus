from pathlib import Path
from tempfile import TemporaryDirectory

import click

from leaf_focus.pipeline.prefect_flow.construct import Construct


@click.command(name="visualise")
@click.option(
    "-v",
    "--visual-file",
    "visualise_path",
    required=True,
    type=Path,
    help="Path to the output visualise image file.",
)
def pipeline_visualise(visualise_path: Path):
    """Visualise all the stages that are run using a pipeline."""
    click.secho("Starting pipeline visualise.", bold=True)
    c = Construct()
    with TemporaryDirectory() as d:
        temp_file = Path(d, "placeholder-file")
        temp_file.touch()
        c.visualise(
            base_dir=d,
            pdf_info_exe=temp_file,
            pdf_text_exe=temp_file,
            pdf_image_exe=temp_file,
            visualise_path=visualise_path,
        )
    click.secho("Finished pipeline visualise.", bold=True)
