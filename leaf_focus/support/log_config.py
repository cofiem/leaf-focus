from importlib.resources import open_text
from logging.config import dictConfig

import yaml


def configure_leaf_focus_logging():
    package = "leaf_focus.resources"
    with open_text(package, "logging.yml", encoding="utf8") as f:
        dictConfig(yaml.safe_load(f))
