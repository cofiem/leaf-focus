import json
from logging import Logger
from pathlib import Path


class Config:
    def __init__(self, logger: Logger, config_file: Path):
        if not logger:
            raise ValueError("Must provide logger.")
        if not config_file:
            raise ValueError("Must provide config file.")
        if not config_file.exists():
            raise ValueError("The config file must exist.")

        self._logger = logger

        with open(config_file, "rt") as f:
            self._config = json.load(f)

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
        return Path(self.get_value("pdf", "items-dir"))

    @property
    def pdf_cache_dir(self):
        return Path(self.get_value("pdf", "cache-dir"))

    @property
    def pdf_base_dir(self):
        return Path(self.get_value("pdf", "base-dir"))

    @property
    def pdf_allowed_domains(self):
        return self.get_value("pdf", "allowed-domains")

    @property
    def pdf_input_urls(self):
        return self.get_value("pdf", "input-urls")

    @property
    def exe_pdf_images_file(self):
        return Path(self.get_value("exe", "pdf-images"))

    @property
    def exe_pdf_info_file(self):
        return Path(self.get_value("exe", "pdf-info"))

    @property
    def exe_pdf_text_file(self):
        return Path(self.get_value("exe", "pdf-text"))

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
