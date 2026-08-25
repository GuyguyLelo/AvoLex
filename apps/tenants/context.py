"""Contexte cabinet courant (ContextVar) pour le filtrage multi-tenant."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.tenants.models import Cabinet

_current_cabinet: ContextVar[Cabinet | None] = ContextVar("current_cabinet", default=None)


def get_current_cabinet() -> Cabinet | None:
    """Retourne le cabinet courant du contexte d'exécution, ou None."""
    return _current_cabinet.get()


def set_current_cabinet(cabinet: Cabinet | None) -> Token[Cabinet | None]:
    """Définit le cabinet courant et retourne le token de reset."""
    return _current_cabinet.set(cabinet)


def reset_current_cabinet(token: Token[Cabinet | None]) -> None:
    """Restaure le cabinet courant à partir d'un token."""
    _current_cabinet.reset(token)


@contextmanager
def cabinet_context(cabinet: Cabinet | None) -> Iterator[Cabinet | None]:
    """Gestionnaire de contexte pour forcer un cabinet (tests, tâches Celery)."""
    token = set_current_cabinet(cabinet)
    try:
        yield cabinet
    finally:
        reset_current_cabinet(token)
