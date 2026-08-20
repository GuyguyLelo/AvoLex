"""Tâches Celery facturation."""

from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def generate_invoice_pdf_task(self: object, invoice_id: str) -> str:
    """Génère et stocke le PDF d'une facture."""
    from apps.billing.models import Invoice
    from apps.billing.services import render_invoice_pdf_bytes, store_invoice_pdf
    from apps.tenants.context import cabinet_context

    try:
        invoice = Invoice.unscoped.select_related("cabinet").get(pk=invoice_id)
    except Invoice.DoesNotExist:
        logger.warning("Facture introuvable pour PDF id=%s", invoice_id)
        return "missing"

    with cabinet_context(invoice.cabinet):
        pdf_bytes = render_invoice_pdf_bytes(invoice)
        store_invoice_pdf(invoice=invoice, pdf_bytes=pdf_bytes)
    logger.info("PDF généré pour facture %s", invoice.number or invoice_id)
    return str(invoice.pk)
