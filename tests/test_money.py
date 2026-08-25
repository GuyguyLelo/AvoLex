"""Tests du formatage monétaire."""

from __future__ import annotations

from decimal import Decimal

from apps.core.money import format_money


def test_format_money_usd_thousands_and_cents() -> None:
    """Les dollars sont préfixés et groupés."""
    assert format_money(Decimal("1234.5"), "USD") == "$1,234.50"
    assert format_money(0) == "$0.00"
    assert format_money("86.4") == "$86.40"
