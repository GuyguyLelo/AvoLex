"""Context processors globaux."""

from __future__ import annotations

from typing import Any

from django.conf import settings
from django.http import HttpRequest


def site_meta(request: HttpRequest) -> dict[str, Any]:
    """Expose le nom du site et des métadonnées UI aux templates."""
    return {
        "SITE_NAME": getattr(settings, "SITE_NAME", "AvoLex"),
        "DEFAULT_CURRENCY": getattr(settings, "DEFAULT_CURRENCY", "USD"),
    }
