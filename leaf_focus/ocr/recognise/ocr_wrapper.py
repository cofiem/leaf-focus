import os


class OcrWrapper:
    """Contain the OCR implementation."""

    # TODO: The ocr recognise likely needs to be done in sequence,
    #       as tensorflow / keras is not easy to parallelise.
    #       Consider separating this out into something similar to the download.
    #       Could compare pre-loaded serial analysis to
    #       pre-loaded multiprocess analysis, on GPU and CPU, see which is faster...

    pipeline = None

    def __init__(self):
        self._construct_pipeline()

    def _construct_pipeline(self):
        if self.pipeline is None:
            # set TF_CPP_MIN_LOG_LEVEL before importing tensorflow
            os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

            import tensorflow as tf

            tf.get_logger().setLevel("WARNING")

            import keras_ocr

            # see: https://github.com/faustomorales/keras-ocr
            # keras-ocr will automatically download pretrained
            # weights for the detector and recognizer.
            self.pipeline = keras_ocr.pipeline.Pipeline()

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state["pipeline"]
        return state

    def __setstate__(self, state):
        # Restore instance attributes.
        self.__dict__.update(state)
        # Restore the pipeline.
        self._construct_pipeline()
