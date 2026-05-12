from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "bot_service",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
    include=["app.tasks.llm_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,

    worker_pool="solo",
    worker_concurrency=1,
    worker_cancel_long_running_tasks_on_connection_loss=False,
    worker_send_task_events=False,
    task_send_sent_event=False,
)