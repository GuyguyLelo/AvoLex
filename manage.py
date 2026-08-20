#!/usr/bin/env python
"""Point d'entrée Django (CLI)."""

from __future__ import annotations

import os
import sys


def main() -> None:
    """Exécute une commande de management Django."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Activez le virtualenv et installez "
            "les dépendances (pip install -r requirements/dev.txt)."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
