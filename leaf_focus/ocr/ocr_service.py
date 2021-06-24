import logging
import os
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np

from leaf_focus.download.items.pdf_item import PdfItem
from leaf_focus.ocr.found_text import FoundText

# set TF_CPP_MIN_LOG_LEVEL before importing tensorflow
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

import tensorflow as tf

tf.get_logger().setLevel("WARNING")

import keras_ocr


class OcrService:
    """Run Optical Character Recognition over images."""

    _original_name = "response_body"
    _text_prefix = "response_body_text"

    _image_prefix = "response_body_image"
    _image_suffix = ".png"

    _ocr_prefix = "response_body_image_ocr"
    _ocr_suffix = ".png"

    _csv_prefix = "response_body_image_found"
    _csv_suffix = ".csv"

    _item_prefix = "items"
    _item_suffix = ".csv"

    def __init__(self, logger: logging.Logger):
        self._logger = logger

        # see: https://github.com/faustomorales/keras-ocr
        # keras-ocr will automatically download pretrained
        # weights for the detector and recognizer.
        self._pipeline = keras_ocr.pipeline.Pipeline()

    def start(self, items_dir: Path, cache_dir: Path):
        if not items_dir.exists() or not items_dir.is_dir():
            self._logger.error(f"Could not find items dir '{items_dir}'.")
            return

        self._logger.info(f"Running OCR using item csv files in '{items_dir}'.")

        pattern = f"{self._item_prefix}*{self._item_suffix}"
        for item_file in items_dir.glob(pattern):
            self.start_item(item_file)

    def start_item(self, item_file: Path):
        if not item_file.exists() or not item_file.is_file():
            self._logger.error(f"Could not find item file '{item_file}'.")
            return

        for item in PdfItem.load(item_file):
            item_path = Path(item.path)

            if not item_path.exists():
                self._logger.error(f"Could not find item path '{item_path}'.")
                return

            parent_dir = item_path.parent

            # find the images of the input item
            pattern = f"{self._image_prefix}*{self._image_suffix}"
            for image_file in parent_dir.glob(pattern):

                if image_file.name.endswith("-ocr.png"):
                    image_file.unlink()
                    continue

                csv_name = image_file.stem.replace(self._image_prefix, self._csv_prefix)
                csv_file = Path(image_file.parent, csv_name + self._csv_suffix)

                ocr_name = image_file.stem.replace(self._image_prefix, self._ocr_prefix)
                ocr_file = Path(image_file.parent, ocr_name + self._ocr_suffix)

                self.start_image(image_file, ocr_file, csv_file)

    def start_image(self, input_file: Path, ocr_file: Path, csv_file: Path):
        if ocr_file.exists() and csv_file.exists():
            self._logger.info(
                f"Not running as OCR output already exists for '{input_file}'."
            )
            return

        self._logger.info(f"Running OCR on '{input_file}'.")

        # read in the image
        images = [
            keras_ocr.tools.read(str(input_file)),
        ]

        # Each list of predictions in prediction_groups is a list of
        # (word, box) tuples.
        prediction_groups = self._pipeline.recognize(images)

        # Plot the predictions
        for image, predictions in zip(images, prediction_groups):
            self.save_figure(ocr_file, image, predictions)
            self.save_predictions(csv_file, predictions)

    def save_figure(
        self,
        path: Path,
        image: Optional[np.ndarray],
        predictions: list[tuple[Any, Any]],
    ):
        self._logger.info(f"Saving OCR image to '{path}'.")

        path.parent.mkdir(exist_ok=True, parents=True)

        fig, ax = plt.subplots(figsize=(20, 20))
        keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)
        fig.savefig(str(path))
        plt.close(fig)

    def save_predictions(self, path: Path, predictions: list[list[tuple[Any, Any]]]):
        self._logger.info(f"Saving OCR result item to '{path}'.")

        # top left, top right, bottom right, bottom left
        # Its structure is [[startX,startY], [endX,startY], [endX,endY], [startX, endY]]
        found_text = []
        for (
            text,
            (
                (top_left_x, top_left_y),
                (top_right_x, top_right_y),
                (bottom_right_x, bottom_right_y),
                (bottom_left_x, bottom_left_y),
            ),
        ) in predictions:
            found_text.append(
                FoundText(
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
            )

        self.order_text_lines(found_text)
        FoundText.save(path, found_text)

    def order_text_lines(self, items: list[FoundText]):
        """Put items into lines of text (top -> bottom, left -> right)."""
        self._logger.info(f"Arranging text into lines.")

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

        # include last items
        if len(current_line) > 0:
            lines.append(current_line)

        # update items to set line number and line order
        for line_index, line in enumerate(lines):
            for item_index, item in enumerate(line):
                item.line_number = line_index + 1
                item.line_order = item_index + 1

        return lines
