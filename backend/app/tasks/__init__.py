# Copyright (c) 2025 CityLens Contributors
# Licensed under the MIT License

"""
Celery Application Configuration
"""

from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "citylens",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.weather_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks to prevent memory leaks
)

# Import tasks to register them (must be after celery_app is created)
# This will register all tasks defined with @shared_task
try:
    from app.tasks import weather_tasks  # noqa: F401, E402
except ImportError:
    # Ignore if weather_tasks not available yet
    pass

