from logging import Logger
from pathlib import Path

from leaf_focus.ocr.recognise.component import Component
from leaf_focus.support.location import Location
from leaf_focus.pdf.identify.item import Item as PdfIdentifyItem
from leaf_focus.pdf.images.item import Item as ImageItem


class Operation:
    """A pipeline building block that creates the ocr recognise files."""

    def __init__(self, logger: Logger, base_path: Path):
        self._logger = logger
        self._base_path = base_path
        self._location = Location(logger)
        self._component = Component(logger)

    def run(self, file_hash: str, page: int, threshold: int):
        """Run the operation."""

        # crate output directory
        loc = self._location
        bd = self._base_path
        input_file = loc.pdf_page_prepared_file(bd, file_hash, page, threshold)
        annotation_file = loc.pdf_page_ocr_file(bd, file_hash, page, threshold)
        predictions_file = loc.pdf_page_text_file(bd, file_hash, page, threshold)

        # create annotation file and predictions file
        self._component.recognise_text(input_file, annotation_file, predictions_file)

        # result
        return annotation_file, predictions_file

    def run_many(self):
        """Run the operation for all the pdfs."""
        for json_path in self._base_path.rglob("pdf-identify.json"):

            # read the pdf identity json file
            pdf_identify = PdfIdentifyItem.read(json_path)
            for pdf_image in ImageItem.load(json_path.parent):
                if pdf_image.variety != "prep":
                    continue
                if pdf_image.threshold is None:
                    continue

                # run the ocr on the prepared image
                self.run(pdf_identify.file_hash, pdf_image.page, pdf_image.threshold)
