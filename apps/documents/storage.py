"""Stockage privé des documents (hors webroot, sans URL publique)."""

from __future__ import annotations

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateDocumentStorage(FileSystemStorage):
    """
    Stockage filesystem hors URL publique.

    Les fichiers sont servis uniquement via des vues authentifiées.
    """

    def __init__(self) -> None:
        super().__init__(
            location=str(settings.MEDIA_ROOT / "documents"),
            base_url=None,
        )

    def url(self, name: str | None) -> str:
        """Refuse toute URL publique dévinable."""
        raise ValueError(
            "Les documents AvoLex n'ont pas d'URL publique ; "
            "utilisez la vue de téléchargement protégée."
        )


private_document_storage = PrivateDocumentStorage()
