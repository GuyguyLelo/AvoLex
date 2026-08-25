"""Formatage des montants (USD par défaut)."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from django.conf import settings

CURRENCY_SYMBOLS: dict[str, str] = {
    "USD": "$",
    "EUR": "€",
    "CAD": "CA$",
    "GBP": "£",
    "HTG": "G",
}


def default_currency() -> str:
    """Code ISO de la devise par défaut du produit."""
    return str(getattr(settings, "DEFAULT_CURRENCY", "USD")).upper()


def format_money(amount: object, currency: str | None = None) -> str:
    """Formate un montant : ``1234.5`` → ``$1,234.50``."""
    if amount is None or amount == "":
        value = Decimal("0.00")
    else:
        try:
            value = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError, TypeError):
            return ""

    code = (currency or default_currency()).upper()
    number = f"{value:,.2f}"
    symbol = CURRENCY_SYMBOLS.get(code, f"{code} ")
    if code == "EUR":
        integer, frac = number.rsplit(".", 1)
        grouped = integer.replace(",", "\u202f")
        return f"{grouped},{frac}\u00a0{symbol}"
    if symbol.endswith(" "):
        return f"{symbol}{number}"
    return f"{symbol}{number}"
