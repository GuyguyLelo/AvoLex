"""Filtres de formatage monétaire."""

from __future__ import annotations

from django import template

from apps.core.money import format_money

register = template.Library()


@register.filter(name="money")
def money_filter(amount: object, currency: str | None = None) -> str:
    """Affiche un montant formaté (dollars par défaut)."""
    code = currency if currency else None
    return format_money(amount, code)
