"""Configuration de l'application subscriptions."""

from __future__ import annotations

from django.apps import AppConfig


class SubscriptionsConfig(AppConfig):
    """AppConfig pour apps.subscriptions."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.subscriptions"
    label = "subscriptions"
    verbose_name = "Abonnements"
