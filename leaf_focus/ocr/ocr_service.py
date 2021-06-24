import logging
import os
from pathlib import Path
from typing import Any, Optional


import matplotlib.pyplot as plt
import numpy as np

from leaf_focus.download.items.pdf_item import PdfItem
from leaf_focus.ocr.found_text import FoundText


class OcrService:
    """Run Optical Character Recognition over images."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

        import tensorflow as tf

        tf.get_logger().setLevel("WARNING")

        import keras_ocr

        # see: https://github.com/faustomorales/keras-ocr
        # keras-ocr will automatically download pretrained
        # weights for the detector and recognizer.
        self._pipeline = keras_ocr.pipeline.Pipeline()

    def start(self, items_dir: Path, cache_dir: Path):
        import keras_ocr

        self._logger.info(f"Running OCR on pdf files.")

        if not items_dir.exists() or not items_dir.is_dir():
            msg = f"Could not find input items dir '{items_dir}'."
            self._logger.error(msg)
            raise ValueError(msg)

        for item_file in items_dir.glob("items*.csv"):

            for item in PdfItem.load(item_file):
                input_image_dir = Path(item.path).parent

                # find the images of the input item
                for input_image_path in input_image_dir.glob(
                    "response_body_image-*.png"
                ):
                    if "-ocr-ocr.png" in input_image_path.name:
                        input_image_path.unlink()
                        continue

                    if "-ocr.png" in input_image_path.name:
                        continue

                    output_csv_path = input_image_path.with_suffix(".csv")
                    output_image_path = Path(
                        input_image_path.parent, input_image_path.stem + "-ocr.png"
                    )

                    if output_image_path.exists() and output_csv_path.exists():
                        self._logger.warning(
                            f"OCR output already exists for '{input_image_path}'."
                        )

                    else:
                        self._logger.info(f"Running OCR on '{input_image_path}'.")

                        # read in the image
                        images = [
                            keras_ocr.tools.read(str(input_image_path)),
                        ]

                        # Each list of predictions in prediction_groups is a list of
                        # (word, box) tuples.
                        prediction_groups = self._pipeline.recognize(images)

                        # Plot the predictions
                        for image, predictions in zip(images, prediction_groups):
                            self.save_figure(output_image_path, image, predictions)
                            self.save_predictions(output_csv_path, predictions)

    def save_figure(
        self,
        path: Path,
        image: Optional[np.ndarray],
        predictions: list[tuple[Any, Any]],
    ):
        self._logger.info(f"Saving OCR results image to '{path}'.")

        import keras_ocr

        fig, ax = plt.subplots(figsize=(20, 20))
        keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)
        fig.savefig(str(path))
        plt.close(fig)

    def iterate_predictions(self, predictions: list[list[tuple[Any, Any]]]):
        # top left, top right, bottom right, bottom left
        # Its structure is [[startX,startY], [endX,startY], [endX,endY], [startX, endY]]
        for (
            text,
            (
                (top_left_x, top_left_y),
                (top_right_x, top_right_y),
                (bottom_right_x, bottom_right_y),
                (bottom_left_x, bottom_left_y),
            ),
        ) in predictions:
            yield FoundText(
                text=text,
                top_left_x=top_left_x,
                top_left_y=top_left_y,
                top_right_x=top_right_x,
                top_right_y=top_right_y,
                bottom_right_x=bottom_right_x,
                bottom_right_y=bottom_right_y,
                bottom_left_x=bottom_left_x,
                bottom_left_y=bottom_left_y,
            )

    def save_predictions(self, path: Path, predictions: list[list[tuple[Any, Any]]]):
        self._logger.info(f"Saving OCR result item to '{path}'.")

        items = list(self.iterate_predictions(predictions))
        FoundText.save(path, items)

    # TODO
    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for item in result:

            # don't process Requests, only process items
            if not isinstance(item, Request):
                adapter = ItemAdapter(item)
                item_file = adapter.get("path")

                # can only process if the item has a path property
                if item_file:
                    pdf_file = Path(item_file)

                    # create images of each page of a pdf file
                    if pdf_file.suffix.lower() == ".pdf":
                        self._run_ocr(pdf_file)

            yield item

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

    def _run_ocr(self, pdf_file: Path):
        if not pdf_file or not pdf_file.exists():
            logger.error(f"Could not find pdf file '{pdf_file}'.")

        pdf_dir = pdf_file.parent
        image_files = pdf_dir.parent.glob("response_body_image*.png")
        for image_file in image_files:
            # don't process ocr images
            if "-ocr.png" in image_file.name:
                continue

            # build output file paths
            csv_file = image_file.with_suffix(".csv")
            ocr_file = Path(image_file.parent, image_file.stem + "-ocr.png")
            if ocr_file.exists() and csv_file.exists():
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"OCR output already exists for '{image_file}'.")
                continue

            logger.info(f"Running OCR on '{image_file}'.")

            # read in the image
            images = [
                keras_ocr.tools.read(str(image_file)),
            ]

            # Each list of predictions in prediction_groups is a list of
            # (word, box) tuples.
            prediction_groups = self._pipeline.recognize(images)

            # Plot the predictions
            for image, predictions in zip(images, prediction_groups):
                self._save_figure(ocr_file, image, predictions)
                self.save_predictions(csv_file, predictions)

    def _save_figure(
        self,
        path: Path,
        image: Optional[np.ndarray],
        predictions: list[tuple[Any, Any]],
    ):
        logger.debug(f"Saving OCR results image to '{path}'.")

        fig, ax = plt.subplots(figsize=(20, 20))
        keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)
        fig.savefig(str(path))
        plt.close(fig)

    def _order_text_lines(self, items: list[FoundText]):
        """Put items into lines of text (top -> bottom, left -> right)."""
        logger.debug(f"Arranging text into lines.")

        lines = []
        current_line = []
        for item in items:
            if not item.is_top_horizontal:
                # exclude items that are too sloped
                continue

            if len(current_line) < 1:
                current_line.append(item)

            elif any([item.is_same_line(i) for i in current_line]):
                current_line.append(item)

            elif len(current_line) > 0:
                # store current line
                current_line = sorted(current_line, key=lambda x: x.top_left)
                lines.append(current_line)

                # create new line
                current_line = [item]

        if len(current_line) > 0:
            lines.append(current_line)

        for line_index, line in enumerate(lines):
            for item_index, item in enumerate(line):
                item.line_number = line_index + 1
                item.line_order = item_index + 1

        return lines
