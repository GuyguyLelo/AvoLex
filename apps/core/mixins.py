"""Mixins UI transverses (fil d'Ariane, etc.)."""

from __future__ import annotations

from typing import Any, ClassVar


class BreadcrumbMixin:
    """Ajoute ``breadcrumb`` au contexte des CBV."""

    breadcrumb: ClassVar[list[dict[str, str]]] = []

    def get_breadcrumb(self) -> list[dict[str, str]]:
        """Retourne les éléments du fil d'Ariane (label, url optionnelle)."""
        return list(self.breadcrumb)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Injecte le fil d'Ariane."""
        context: dict[str, Any] = super().get_context_data(**kwargs)  # type: ignore[misc]
        context["breadcrumb"] = self.get_breadcrumb()
        return context
