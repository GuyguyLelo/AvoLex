"""Configuration de l'application documents."""

from __future__ import annotations

from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    """AppConfig pour apps.documents."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.documents"
    label = "documents"
    verbose_name = "Documents"
