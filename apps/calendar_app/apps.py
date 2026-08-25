"""Configuration de l'application calendar_app."""

from __future__ import annotations

from django.apps import AppConfig


class CalendarAppConfig(AppConfig):
    """AppConfig pour apps.calendar_app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.calendar_app"
    label = "calendar_app"
    verbose_name = "Agenda"
