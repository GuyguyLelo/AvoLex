"""Configuration de l'application API."""

from __future__ import annotations

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """AppConfig pour apps.api."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"
    label = "api"
    verbose_name = "API"
