"""Settings pytest — isolation, rapidité, pas de services externes requis."""

from __future__ import annotations

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"

# PostgreSQL de test via DATABASE_URL ; fallback sqlite uniquement si forcé
# Par défaut on utilise la même DB URL que le .env (CI fournit Postgres).
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "avolex-tests",
    },
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

AXES_ENABLED = False

# WeasyPrint nécessite Pango/GTK (installés en CI Linux, pas toujours sous Windows).
BILLING_PDF_BACKEND = "stub"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
