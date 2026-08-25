"""Configuration de l'application matters."""

from __future__ import annotations

from django.apps import AppConfig


class MattersConfig(AppConfig):
    """AppConfig pour apps.matters."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.matters"
    label = "matters"
    verbose_name = "Dossiers"
