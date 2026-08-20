"""Configuration de l'application accounts."""

from __future__ import annotations

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """AppConfig pour apps.accounts."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
    verbose_name = "Comptes"
