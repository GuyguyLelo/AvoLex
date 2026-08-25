"""Settings production — sécurité renforcée."""

from __future__ import annotations
from django.core.exceptions import ImproperlyConfigured
from .base import *  # noqa: F403
from .base import env
import os

DEBUG = False

SECRET_KEY = env("SECRET_KEY")
if not SECRET_KEY or SECRET_KEY.startswith("dev-"):
    raise ImproperlyConfigured("SECRET_KEY de production invalide.")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS doit être défini en production.")

# Sécurité SSL (désactivée pour le test)
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = env.bool("USE_X_FORWARDED_HOST", default=True)

SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=False)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

# Email
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)

CELERY_TASK_ALWAYS_EAGER = False

# Pour servir l'application sous le chemin /avolex/
FORCE_SCRIPT_NAME = '/avolex'
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Redéfinir STATIC_URL et MEDIA_URL avec FORCE_SCRIPT_NAME
STATIC_URL = f"{FORCE_SCRIPT_NAME}/static/"
MEDIA_URL = f"{FORCE_SCRIPT_NAME}/media/"
