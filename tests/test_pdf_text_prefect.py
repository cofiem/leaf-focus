from leaf_focus.pdf.text.prefect_task import PdfTextTask
from tests.base_test import BaseTest


class TestPdfTextPrefect(BaseTest):
    def test_instance(self, tmp_path):
        tmp_file = tmp_path / "example"
        tmp_file.touch()
        PdfTextTask(tmp_path, tmp_file)
