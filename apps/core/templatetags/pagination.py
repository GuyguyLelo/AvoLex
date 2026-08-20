"""Filtres de pagination."""

from __future__ import annotations

from typing import Any

from django import template

register = template.Library()


@register.filter
def elided_page_range(page_obj: Any) -> list[Any]:
    """Pages compactes : 1 … 4 5 6 … 12."""
    if page_obj is None:
        return []
    paginator = page_obj.paginator
    return list(paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1))
