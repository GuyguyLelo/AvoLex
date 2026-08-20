"""Configuration de l'application billing."""

from __future__ import annotations

from django.apps import AppConfig


class BillingConfig(AppConfig):
    """AppConfig pour apps.billing."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.billing"
    label = "billing"
    verbose_name = "Facturation"
