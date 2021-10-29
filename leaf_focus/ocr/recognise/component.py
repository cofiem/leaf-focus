import os
from logging import Logger
from pathlib import Path
from typing import Any, Optional, Iterable

import numpy as np

from leaf_focus.ocr.recognise.item import Item as TextItem


class Component:
    """Run image OCR and save the output."""

    def __init__(self, logger: Logger):
        self._logger = logger
        self._pipeline = None

        self._construct_pipeline()

    def _construct_pipeline(self):
        if self._pipeline is None:
            # set TF_CPP_MIN_LOG_LEVEL before importing tensorflow
            os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

            import tensorflow as tf

            tf.get_logger().setLevel("WARNING")

            import keras_ocr

            # see: https://github.com/faustomorales/keras-ocr
            # keras-ocr will automatically download pretrained
            # weights for the detector and recognizer.
            self._pipeline = keras_ocr.pipeline.Pipeline()

    def recognise_text(
        self,
        image_file: Path,
        annotation_file: Path,
        predictions_file: Path,
    ) -> None:
        """Recognise the text in an image and save the text and image annotations."""

        if not image_file:
            raise ValueError("Must supply image file.")
        if not annotation_file:
            raise ValueError("Must supply annotation file.")
        if not predictions_file:
            raise ValueError("Must supply predictions file.")
        if not image_file.exists():
            raise FileNotFoundError(f"Image file does not exist '{image_file}'.")

        if annotation_file.exists() and predictions_file.exists():
            self._log_debug(f"OCR output already exists for '{image_file}'.")
            return

        self._log_info(f"Running OCR on '{image_file}'.")

        # read in the image
        import keras_ocr

        images = [
            keras_ocr.tools.read(str(image_file)),
        ]

        # Each list of predictions in prediction_groups is a list of
        # (word, box) tuples.
        prediction_groups = self._pipeline.recognize(images)

        # Plot the predictions
        for image, predictions in zip(images, prediction_groups):
            self.save_figure(annotation_file, image, predictions)
            items = self.convert_predictions(predictions)
            self.save_items(predictions_file, items)

    def save_figure(
        self,
        annotation_file: Path,
        image: Optional[np.ndarray],
        predictions: list[tuple[Any, Any]],
    ):
        """Save the annotated image."""

        if not annotation_file:
            raise ValueError("Must supply annotation file.")
        if image is None or image.size < 1 or len(image.shape) != 3:
            msg_image = image.shape if image is not None else None
            raise ValueError(f"Must supply valid image data, not '{msg_image}'.")
        if not predictions:
            raise ValueError("Must supply predictions data.")

        self._log_info(f"Saving OCR image to '{annotation_file}'.")

        import matplotlib.pyplot as plt

        annotation_file.parent.mkdir(exist_ok=True, parents=True)

        fig, ax = plt.subplots(figsize=(20, 20))
        import keras_ocr

        keras_ocr.tools.drawAnnotations(image=image, predictions=predictions, ax=ax)
        fig.savefig(str(annotation_file))
        plt.close(fig)

    def convert_predictions(self, predictions: list[tuple[Any, Any]]):
        """Convert predictions to items."""
        if not predictions:
            raise ValueError("Must supply predictions data.")

        for prediction in predictions:
            yield TextItem.from_prediction(prediction)

    def save_items(self, items_file: Path, items: Iterable[TextItem]):
        """Save items to csv file."""
        if not items_file:
            raise ValueError("Must supply predictions file.")
        if not items:
            raise ValueError("Must supply predictions data.")

        self._log_info(f"Saving OCR predictions to '{items_file}'.")

        items_list = list(items)

        # order_text_lines sets the line number and line order
        self.order_text_lines(items_list)
        TextItem.save(items_file, items_list)

    def order_text_lines(self, items: Iterable[TextItem]):
        """Put items into lines of text (top -> bottom, left -> right)."""
        if not items:
            raise ValueError("Must supply items.")

        self._log_debug("Arranging text into lines.")

        lines = []
        current_line = []
        for item in items:
            if not item.is_horizontal_level:
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

    def _log_debug(self, message: str):
        self._logger.debug(message)

    def _log_info(self, message: str):
        self._logger.info(message)
