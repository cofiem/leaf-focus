import os
from logging import Logger
from pathlib import Path

from celery import chain, group

from leaf_focus.components.data.identify_item import IdentifyItem
from leaf_focus.components.data.pdf_item import PdfItem
from leaf_focus.support.config import Config


class Pipeline:

    command = "pipeline"
    description = "Run the pdf processing pipeline."

    def build(self, sub_parser) -> None:
        """Build the command line."""
        sub_parser.add_argument(
            "operation",
            choices=["pdf-identify", "pdf-extract", "ocr-process"],
            help="The pipeline operation to start.",
        )

    def run(self, parsed_args, logger: Logger):
        """Run using the parsed args."""
        config_file = parsed_args.config_file  # type: Path
        operation = parsed_args.operation  # type: str

        if not config_file:
            raise ValueError("Must provide config file.")
        if not config_file.exists():
            raise ValueError(f"Config file must exist '{config_file}'.")

        config = Config(config_file)

        # the celery app expects to find the config file from an env var 'LEAF_FOCUS_CONFIG_FILE'
        # so, set this env var
        os.environ["LEAF_FOCUS_CONFIG_FILE"] = str(config_file)

        # find the scrapy output items and create background tasks for each item
        if operation == "pdf-identify":
            self._pdf_identify(logger, config.pdf_items_dir)
        elif operation == "pdf-extract":
            self._pdf_extract(logger, config.pdf_items_dir, config.pdf_data_dir)
        elif operation == "ocr-process":
            self._ocr_process(
                logger,
                config.pdf_items_dir,
                config.pdf_data_dir,
                config.image_threshold,
            )
        else:
            raise ValueError(f"Unknown operation '{operation}'.")

    def _pdf_identify(self, logger: Logger, items_dir: Path):

        logger.info(f"Starting pdf identify.")

        from leaf_focus.pipeline.pdf.identify import pdf_identify

        for path in items_dir.glob("*.csv"):
            if not path.is_file():
                continue
            items = PdfItem.load(path)
            for item in items:
                pdf_identify.delay(item.path, item.name)

        logger.info(f"Finished enqueuing pdf identify tasks.")

    def _pdf_extract(self, logger: Logger, items_dir: Path, data_dir: Path):
        logger.info(f"Starting pdf extract.")

        from leaf_focus.pipeline.pdf.info import pdf_info
        from leaf_focus.pipeline.pdf.text import pdf_text
        from leaf_focus.pipeline.pdf.images import pdf_images

        pdf_files = {}

        for path in items_dir.rglob("*.csv"):
            items = PdfItem.load(path)
            for item in items:
                if item.path not in pdf_files:
                    pdf_files[item.path] = item
                else:
                    raise ValueError(f"Item path has already been seen '{item.path}'.")

        for path in data_dir.rglob("pdf-identify.json"):
            identify = IdentifyItem.read(path)
            pdf_file = str(identify.pdf_file)
            file_hash = identify.file_hash
            name = pdf_files[pdf_file].name

            group(
                pdf_info.si(pdf_file, file_hash, name),
                pdf_text.si(pdf_file, file_hash, name),
                pdf_images.si(pdf_file, file_hash, name),
            ).delay()

        logger.info(f"Finished enqueuing pdf extract tasks.")

    def _ocr_process(
        self, logger: Logger, items_dir: Path, data_dir: Path, threshold: int
    ):
        logger.info(f"Starting ocr process.")

        from leaf_focus.pipeline.ocr.prepare import ocr_prepare
        from leaf_focus.pipeline.ocr.recognise import ocr_recognise
        from leaf_focus.components.data.image_item import ImageItem

        pdf_files = {}

        for path in items_dir.rglob("*.csv"):
            items = PdfItem.load(path)
            for item in items:
                if item.path not in pdf_files:
                    pdf_files[item.path] = item
                else:
                    raise ValueError(f"Item path has already been seen '{item.path}'.")

        for path in data_dir.rglob("pdf-identify.json"):
            identify = IdentifyItem.read(path)
            pdf_file = str(identify.pdf_file)
            file_hash = identify.file_hash

            pdf_item = pdf_files[pdf_file]
            name = pdf_item.name

            images = ImageItem.load(path.parent)
            for image in images:
                if image.page is None:
                    continue
                if image.threshold is not None:
                    continue
                if image.variety is not None:
                    continue

                chain(
                    ocr_prepare.si(file_hash, name, image.page, threshold),
                    ocr_recognise.si(file_hash, name, image.page, threshold),
                ).delay()

                raise ValueError(
                    f"Stop: {repr(identify)} - {repr(pdf_item)} - {repr(image)}"
                )

        logger.info(f"Finished enqueuing ocr process tasks.")
