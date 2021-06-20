import logging
from pathlib import Path
from typing import Any, Optional


import matplotlib.pyplot as plt
import numpy as np

from leaf_focus.text.found_text import FoundText


class OCRService:
    def __init__(self, logger: logging.Logger):
        self._logger = logger

        # see: https://github.com/faustomorales/keras-ocr
        # keras-ocr will automatically download pretrained
        # weights for the detector and recognizer.
        import keras_ocr

        self._pipeline = keras_ocr.pipeline.Pipeline()

    def start(
        self,
        input_image_path: Path,
        output_image_path: Path,
        output_csv_path: Path,
    ):
        self._logger.info(f"Running OCR on pdf files.")

        if not input_image_path.exists():
            msg = f"Could not find input image '{input_image_path}'."
            self._logger.error(msg)
            raise ValueError(msg)

        if not output_image_path.exists() or not output_csv_path.exists():
            self._logger.info(f"Running OCR on '{input_image_path}'.")

            import keras_ocr

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
        else:
            self._logger.warning(f"OCR output already exists for '{input_image_path}'.")

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
