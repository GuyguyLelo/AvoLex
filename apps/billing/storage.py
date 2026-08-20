"""Stockage privé des PDF de factures."""

from __future__ import annotations

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateInvoiceStorage(FileSystemStorage):
    """PDF hors webroot, sans URL publique."""

    def __init__(self) -> None:
        super().__init__(
            location=str(settings.MEDIA_ROOT / "invoices"),
            base_url=None,
        )

    def url(self, name: str | None) -> str:
        """Refuse toute URL publique."""
        raise ValueError(
            "Les factures PDF n'ont pas d'URL publique ; "
            "utilisez la vue de téléchargement protégée."
        )


private_invoice_storage = PrivateInvoiceStorage()
