import logging
import os
import re
from pathlib import Path
from typing import Any, Optional, List, Tuple

from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

from leaf_focus.components.download.pdf_item import PdfItem
from leaf_focus.ocr.found_text import FoundText


class OcrService:
    """Run Optical Character Recognition over images."""

    _item_prefix = "items"
    _item_suffix = ".csv"

    _image_prefix = "response_body_image-"
    _image_pattern = re.compile(rf"^{_image_prefix}\d+\.png$")

    _image_suffix = ".png"
    _csv_suffix = ".csv"

    _threshold_id = "threshold"
    _ocr_id = "ocr"
    _csv_id = "found-text"

    def __init__(self, logger: logging.Logger):
        self._logger = logger

        # set TF_CPP_MIN_LOG_LEVEL before importing tensorflow
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

        import tensorflow as tf

        tf.get_logger().setLevel("WARNING")

        import keras_ocr

        # see: https://github.com/faustomorales/keras-ocr
        # keras-ocr will automatically download pretrained
        # weights for the detector and recognizer.
        self._pipeline = keras_ocr.pipeline.Pipeline()

    def start(self, items_dir: Path, cache_dir: Path):
        """
        Process the cached pdf page images:

        - convert to black and white by thresholding image - threshold_image
        - run OCR over the image - recognise_text
        - save the found text and rectangle to a csv file - save_predictions
        - save the found text and rectangle to an image - save_figure
        :param items_dir: The directory containing scrapy output items csv files.
        :param cache_dir: The directory containing the scrapy cache files.
        """
        if not items_dir.exists() or not items_dir.is_dir():
            self._logger.error(f"Could not find items dir '{items_dir}'.")
            return

        self._logger.info(f"Running OCR using item csv files in '{items_dir}'.")

        pattern = f"{self._item_prefix}*{self._item_suffix}"
        for item_file in items_dir.glob(pattern):
            self.process_item(item_file)

    def process_item(self, item_file: Path):
        if not item_file.exists() or not item_file.is_file():
            self._logger.error(f"Could not find item file '{item_file}'.")
            return

        for item in PdfItem.load(item_file):
            item_path = Path(item["path"])

            if not item_path.exists():
                self._logger.error(f"Could not find item path '{item_path}'.")
                return

            parent_dir = item_path.parent

            # find the images of the input item
            pattern = f"{self._image_prefix}*{self._image_suffix}"
            for image_file in parent_dir.glob(pattern):
                match = self._image_pattern.fullmatch(image_file.name)
                if not match:
                    continue

                name = image_file.stem
                threshold_file = parent_dir / self._build_name(
                    name, self._threshold_id, self._image_suffix
                )
                ocr_file = parent_dir / self._build_name(
                    name, self._ocr_id, self._image_suffix
                )
                csv_file = parent_dir / self._build_name(
                    name, self._csv_id, self._csv_suffix
                )

                self.recognise_text(image_file, threshold_file, ocr_file, csv_file)

    def recognise_text(
        self, input_file: Path, threshold_file: Path, ocr_file: Path, csv_file: Path
    ):
        if threshold_file.exists() and ocr_file.exists() and csv_file.exists():
            self._logger.info(
                f"Not running OCR as output already exists for '{input_file}'."
            )
            return

        self._logger.info(f"Running OCR on '{input_file}'.")

        # create the threshold image
        self.threshold_image(input_file, threshold_file, threshold=190)

        # read in the image
        import keras_ocr

        images = [
            keras_ocr.tools.read(str(threshold_file)),
        ]

        # Each list of predictions in prediction_groups is a list of
        # (word, box) tuples.
        prediction_groups = self._pipeline.recognize(images)

        # Plot the predictions
        for image, predictions in zip(images, prediction_groups):
            self.save_figure(ocr_file, image, predictions)
            self.save_predictions(csv_file, predictions)

    def threshold_image(self, input_file: Path, output_file: Path, threshold: int):
        img = Image.open(input_file)

        def calc_threshold(value):
            return 255 if value > threshold else 0

        r = img.convert("L").point(calc_threshold, mode="1")
        r.save(output_file)

    def save_figure(
        self,
        path: Path,
        image: Optional[np.ndarray],
        predictions: List[Tuple[Any, Any]],
    ):
        self._logger.debug(f"Saving OCR image to '{path}'.")

        path.parent.mkdir(exist_ok=True, parents=True)

        fig, ax = plt.subplots(figsize=(20, 20))
        import keras_ocr

        keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)
        fig.savefig(str(path))
        plt.close(fig)

    def save_predictions(self, path: Path, predictions: list[list[tuple[Any, Any]]]):
        self._logger.debug(f"Saving OCR predictions to '{path}'.")

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
        self._logger.debug(f"Arranging text into lines.")

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

    def _build_name(self, prefix: str, middle: str, suffix: str):
        prefix = prefix.strip("-")
        middle = middle.strip("-")
        suffix = suffix if suffix.startswith(".") else "." + suffix
        return "-".join([prefix, middle]) + suffix
