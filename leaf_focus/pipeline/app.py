import os
from pathlib import Path

from celery import Celery
from celery.utils.log import get_task_logger

from leaf_focus.support.config import Config

logger = get_task_logger("leaf-focus")

_config_str = os.getenv("LEAF_FOCUS_CONFIG_FILE")

if not _config_str:
    raise ValueError("Must provide 'LEAF_FOCUS_CONFIG_FILE'.")

_config_file = Path(_config_str)
if not _config_file.exists():
    raise ValueError(f"The config file must exist '{_config_file}'.")

config = Config(logger, _config_file)

app = Celery(
    main="leaf-focus",
    broker=config.process_broker,
    backend=config.process_backend,
    include=[
        "leaf_focus.pipeline.ocr.prepare",
        "leaf_focus.pipeline.ocr.recognise",
        "leaf_focus.pipeline.pdf.identify",
        "leaf_focus.pipeline.pdf.images",
        "leaf_focus.pipeline.pdf.info",
        "leaf_focus.pipeline.pdf.text",
    ],
)

app.conf.update(result_expires=3600, task_track_started=True)

app.conf.task_default_queue = config.process_default_queue
app.conf.task_routes = config.process_task_queues


a = {
    "p": "",
    "name": "leaf-focus.node.work.1",
    "prefix": "",
    "suffix": "ubuntu2004.localdomain",
    "cmd": None,
    "append": "",
    "options": {
        "--events": None,
        "--queues": None,
        "--pidfile": None,
        "--logfile": None,
        "--loglevel": None,
        "--time-limit": "3600",
        "--concurrency": "2",
        "--app": None,
    },
}
