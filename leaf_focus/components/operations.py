import json
from logging import Logger
from pathlib import Path

from leaf_focus.components.ocr.prepare import Prepare
from leaf_focus.components.ocr.recognise import Recognise
from leaf_focus.components.pdf.images import Images
from leaf_focus.components.pdf.info import Info
from leaf_focus.components.pdf.text import Text
from leaf_focus.components.store.identify import Identify
from leaf_focus.components.store.location import Location


class Operations:
    def __init__(self, logger: Logger, config_file: Path):
        self._logger = logger

        with open(config_file, "rt") as f:
            self._config = json.load(f)

        self.identify = Identify(logger)
        self.location = Location(logger)
        self.base_dir = Path(self.get_value("pdf", "base-dir"))

        self._pdf_images = Images(Path(self.get_value("exe", "pdf-images")), logger)
        self._pdf_info = Info(Path(self.get_value("exe", "pdf-info")), logger)
        self._pdf_text = Text(Path(self.get_value("exe", "pdf-text")), logger)
        self._prepare = Prepare(logger)
        self._recognise = Recognise(logger)

    @property
    def image_threshold(self):
        return self.get_value("ocr", "threshold")

    @property
    def process_broker(self):
        return self.get_value("process", "broker")

    @property
    def process_backend(self):
        return self.get_value("process", "backend")

    @property
    def process_task_queues(self):
        return self.get_value("process", "task-queues")

    @property
    def process_default_queue(self):
        return self.get_value("process", "default-queue")

    @property
    def pdf_items_dir(self):
        return self.get_value("pdf", "items-dir")

    @property
    def pdf_cache_dir(self):
        return self.get_value("pdf", "cache-dir")

    @property
    def pdf_allowed_domains(self):
        return self.get_value("pdf", "allowed-domains")

    @property
    def pdf_input_urls(self):
        return self.get_value("pdf", "input-urls")

    def pdf_identify(self, details_file: Path, base_dir: Path):
        """Create the pdf identify file containing file hash details."""

        # load the details file
        with open(details_file, "rt") as f:
            details = json.load(f)

        # get the hash of the source file
        path = details.get("path")
        file_hash = self.identify.file_hash(path)

        # get the hash and hash type to the details
        identify = {
            "pdf_file": str(path),
            "hash_type": self.identify.file_hash_type,
            "file_hash": file_hash,
        }

        # get the path to write the identify file
        output_file = self.location.identify_file(base_dir, file_hash)

        # write the identify file as json
        with open(output_file, "wt") as f:
            json.dump(identify, f)

        return output_file

    def pdf_images(self, pdf_identify_file: Path):
        """Create the pdf image files."""

        # read the identify file
        with open(pdf_identify_file, "rt") as f:
            identify = json.load(f)

        # create the pdf page images
        input_file = Path(identify.get("pdf_file"))
        file_hash = identify.get("file_hash")
        output_prefix = self.location.pdf_images_path(self.base_dir, file_hash)
        self.location.create_directory(output_prefix.parent)
        pdf_image_files = self._pdf_images.create(input_file, output_prefix)

        return pdf_image_files

    def pdf_info(self, pdf_identify_file: Path):
        """Create the pdf info file."""

        # read the identify file
        with open(pdf_identify_file, "rt") as f:
            identify = json.load(f)

        # create the pdf info file
        input_file = Path(identify.get("pdf_file"))
        file_hash = identify.get("file_hash")
        output_file = self.location.pdf_info_file(self.base_dir, file_hash)
        self.location.create_directory(output_file.parent)
        self._pdf_info.create(input_file, output_file)

        return output_file

    def pdf_text(self, pdf_identify_file: Path):
        """Create the pdf text file."""

        # read the identify file
        with open(pdf_identify_file, "rt") as f:
            identify = json.load(f)

        # create the pdf text file
        input_file = Path(identify.get("pdf_file"))
        file_hash = identify.get("file_hash")
        output_file = self.location.pdf_text_file(self.base_dir, file_hash)
        self.location.create_directory(output_file.parent)
        self._pdf_text.create(input_file, output_file)

        return output_file

    def ocr_prepare(self, pdf_identify_file: Path, threshold: int, page: int):
        """Create the image file ready for OCR."""

        # read the identify file
        with open(pdf_identify_file, "rt") as f:
            identify = json.load(f)

        # create the image file
        loc = self.location
        bd = self.base_dir
        file_hash = identify.get("file_hash")
        input_file = loc.pdf_page_image_file(bd, file_hash, page)
        output_file = loc.pdf_page_prepared_file(bd, file_hash, threshold, page)

        self._prepare.threshold(input_file, output_file, threshold)

        return output_file

    def ocr_recognise(self, pdf_identify_file: Path, threshold: int, page: int):
        """ "Run image OCR and save the output."""

        # read the identify file
        with open(pdf_identify_file, "rt") as f:
            identify = json.load(f)

        # create the image file
        loc = self.location
        bd = self.base_dir
        file_hash = identify.get("file_hash")
        input_file = loc.pdf_page_image_file(bd, file_hash, page)
        annotation_file = loc.pdf_page_ocr_file(bd, file_hash, threshold, page)
        predictions_file = loc.pdf_page_text_file(bd, file_hash, threshold, page)

        self._recognise.recognise_text(input_file, annotation_file, predictions_file)

        return annotation_file, predictions_file

    def get_value(self, *args: str):
        """Get a value from the config data."""
        if not args:
            raise ValueError("Tried to get a value with no args.")

        full_args = ".".join([i for i in args])

        current = self._config
        last_index = len(args) - 1
        for index, arg in enumerate(args):
            if index < last_index:
                current_keys = current.keys()
                current = current.get(arg, {})
            else:
                current_keys = current.keys()
                current = current.get(arg, None)

            if current is None:
                available_keys = ", ".join(sorted(current_keys))
                raise ValueError(
                    f"Could not find entry for '{arg}' in '{full_args}'. "
                    f"Available entries at this point are '{available_keys}'."
                )

        result = current  # type: str
        return result
