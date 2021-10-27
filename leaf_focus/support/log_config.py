from importlib.resources import open_text
from logging.config import dictConfig

import yaml


def configure_leaf_focus_logging():
    package = "leaf_focus.resources"
    with open_text(package, "logging.yaml") as f:
        dictConfig(yaml.safe_load(f))
