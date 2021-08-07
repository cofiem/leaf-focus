from celery import Celery

app = Celery(
    "leaf-focus",
    broker="amqp://guest:guest@localhost:5672/",
    backend="elasticsearch://localhost:9200/leaf-focus/tasks",
    include=["leaf_focus.pipeline.tasks"],
)

app.conf.update(result_expires=3600, task_track_started=True)
