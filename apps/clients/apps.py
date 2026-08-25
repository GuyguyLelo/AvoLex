"""Configuration de l'application clients."""

from __future__ import annotations

from django.apps import AppConfig


class ClientsConfig(AppConfig):
    """AppConfig pour apps.clients."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.clients"
    label = "clients"
    verbose_name = "Clients"
