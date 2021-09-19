from pathlib import Path

from prefect import Task

from leaf_focus.pdf.identify.operation import Operation


class PrefectTask(Task):
    """A Prefect task to run the pdf identify operation."""

    def __init__(self, base_path: Path, **kwargs):
        super().__init__(**kwargs)
        self._operation = Operation(self.logger, base_path)

    # noinspection PyMethodOverriding
    def run(self, pdf_file: str):
        """Run the task."""

        pdf_path = Path(pdf_file)
        pdf_identify_path = self._operation.run(pdf_path)
        return str(pdf_identify_path)
