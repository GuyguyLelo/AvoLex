"""Package de configuration AvoLex (settings, URLs, Celery)."""

from .celery import app as celery_app

__all__ = ("celery_app",)
