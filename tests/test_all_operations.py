import logging
import pytest
from pathlib import Path

from leaf_focus.ocr.prepare.operation import Operation as PrepareOperation
from leaf_focus.ocr.recognise.operation import Operation as RecogniseOperation
from leaf_focus.pdf.identify.item import Item as IdentifyItem
from leaf_focus.pdf.identify.operation import Operation as IdentifyOperation
from leaf_focus.pdf.images.operation import Operation as ImageOperation
from leaf_focus.pdf.info.operation import Operation as InfoOperation
from leaf_focus.pdf.text.operation import Operation as TextOperation
from tests.base_test import BaseTest


class TestAllOperations(BaseTest):
    @pytest.mark.slow
    def test_flow(self, tmp_path, caplog, exe_pdf_info, exe_pdf_text, exe_pdf_image):
        caplog.set_level(logging.INFO)
        logger = logging.getLogger()
        pdf_path = self.example1_path(".pdf")
        hash_dir = self.example1_hash_dir(".pdf")

        base_path = tmp_path

        # pdf identify
        identify = IdentifyOperation(logger, base_path)
        identify_path = identify.run(pdf_path)

        assert identify_path == base_path / hash_dir / "pdf-identify.json"
        assert caplog.record_tuples[0] == (
            "root",
            logging.INFO,
            f"Creating pdf identify for cache id '{pdf_path.parts[-2]}'.",
        )
        assert len(caplog.record_tuples) == 1

        file_hash = IdentifyItem.read(identify_path).file_hash

        # pdf info
        info = InfoOperation(logger, base_path, exe_pdf_info)
        info_path = info.run(pdf_path, file_hash)

        assert info_path == base_path / hash_dir / "pdf-info.json"
        assert caplog.record_tuples[1] == (
            "root",
            logging.INFO,
            f"Creating pdf info for '{pdf_path}'.",
        )
        assert len(caplog.record_tuples) == 2

        # pdf text
        text = TextOperation(logger, base_path, exe_pdf_text)
        text_path = text.run(pdf_path, file_hash)

        assert text_path == base_path / hash_dir / "pdf-text.txt"
        assert caplog.record_tuples[2] == (
            "root",
            logging.INFO,
            f"Creating pdf text for '{pdf_path}'.",
        )
        assert len(caplog.record_tuples) == 3

        # pdf images
        image = ImageOperation(logger, base_path, exe_pdf_image)
        image_path = image.run(pdf_path, file_hash)

        assert image_path == [Path(base_path / hash_dir / "pdf-page-000001.png")]
        assert caplog.record_tuples[3] == (
            "root",
            logging.INFO,
            f"Creating pdf page images for cache id '{pdf_path.parts[-2]}'.",
        )
        assert len(caplog.record_tuples) == 4

        page = 1
        threshold = 190

        # ocr prepare
        prepare = PrepareOperation(logger, base_path)
        prepare_path = prepare.run(file_hash, page, threshold)

        assert (
            prepare_path
            == base_path / hash_dir / f"pdf-page-00000{page}-prep-th-{threshold}.png"
        )
        assert caplog.record_tuples[4] == (
            "root",
            logging.INFO,
            f"Creating threshold image for '{image_path[0].parts[-2]}' '{image_path[0].name}'.",
        )
        assert len(caplog.record_tuples) == 5

        # ocr recognise
        recognise = RecogniseOperation(logger, base_path)
        a_path, p_path = recognise.run(file_hash, page, threshold)

        assert a_path == base_path / hash_dir / "pdf-page-000001-ocr-th-190.png"
        assert p_path == base_path / hash_dir / "pdf-page-000001-text-th-190.csv"

        assert caplog.record_tuples[5:] == [
            (
                "root",
                logging.INFO,
                f"Running OCR on '{prepare_path}'.",
            ),
            (
                "root",
                logging.INFO,
                f"Saving OCR image to '{a_path}'.",
            ),
            (
                "root",
                logging.INFO,
                f"Saving OCR predictions to '{p_path}'.",
            ),
        ]
        assert len(caplog.record_tuples) == 8
