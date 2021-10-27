import os

from prefect import resource_manager


@resource_manager
class OcrResource:
    pipeline = None

    def __init__(self):
        """
        Initialize the resource manager.
        Store any values required by the setup and cleanup steps.
        """
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

    def setup(self):
        """
        Setup the resource.
        The result of this method can be used in downstream tasks.
        """
        return self.pipeline

    def cleanup(self, resource):
        """
        Cleanup the resource.
        Receives the result of `setup`, and is always called if `setup` succeeds,
        even if other upstream tasks failed.
        """
        pass

    # def __getstate__(self):
    #     # Copy the object's state from self.__dict__ which contains
    #     # all our instance attributes. Always use the dict.copy()
    #     # method to avoid modifying the original state.
    #     state = self.__dict__.copy()
    #     # Remove the unpicklable entries.
    #     del state["pipeline"]
    #     return state
    #
    # def __setstate__(self, state):
    #     # Restore instance attributes.
    #     self.__dict__.update(state)
    #     # Restore the pipeline.
    #     self._construct_pipeline()
