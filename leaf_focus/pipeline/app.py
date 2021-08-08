import os
from pathlib import Path

from celery import Celery
from celery.utils.log import get_task_logger

from leaf_focus.components.operations import Operations

logger = get_task_logger("leaf-focus")

operations = Operations(logger, Path(os.getenv("LEAF_FOCUS_CONFIG_FILE")))

app = Celery(
    main="leaf-focus",
    broker=operations.process_broker,
    backend=operations.process_backend,
    include=["leaf_focus.pipeline.tasks"],
)

app.conf.update(result_expires=3600, task_track_started=True)

app.conf.task_default_queue = operations.process_default_queue
app.conf.task_routes = operations.process_task_queues
