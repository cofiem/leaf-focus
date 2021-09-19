from pathlib import Path

from prefect import Task

from leaf_focus.pdf.images.operation import Operation


class PrefectTask(Task):
    """A Prefect task to run the pdf images operation."""

    def __init__(self, base_path: Path, exe_path: Path, **kwargs):
        super().__init__(**kwargs)
        self._operation = Operation(self.logger, base_path, exe_path)

    # noinspection PyMethodOverriding
    def run(self, pdf_file: str, file_hash: str):
        """Run the task."""

        pdf_path = Path(pdf_file)
        pdf_image_paths = self._operation.run(pdf_path, file_hash)
        return [{"path": str(p), "page": n} for p, n in pdf_image_paths]
