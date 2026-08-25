"""Tâches Celery agenda — rappels e-mail."""

from __future__ import annotations

import logging

from django.core.mail import send_mail
from django.utils import timezone

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def send_due_event_reminders() -> int:
    """Envoie les rappels dont l'échéance est passée."""
    from apps.calendar_app.services import pending_reminders

    sent = 0
    for event in pending_reminders():
        recipient = None
        if event.assigned_to and event.assigned_to.email:
            recipient = event.assigned_to.email
        if not recipient:
            event.reminder_sent_at = timezone.now()
            event.save(update_fields=["reminder_sent_at", "updated_at"])
            continue
        subject = f"[AvoLex] Rappel : {event.title}"
        body = (
            f"Événement : {event.title}\n"
            f"Type : {event.get_event_type_display()}\n"
            f"Début : {event.starts_at}\n"
            f"Lieu : {event.location or '—'}\n"
        )
        if event.matter_id:
            body += f"Dossier : {event.matter}\n"
        try:
            send_mail(subject, body, None, [recipient], fail_silently=False)
            event.reminder_sent_at = timezone.now()
            event.save(update_fields=["reminder_sent_at", "updated_at"])
            sent += 1
        except Exception:
            logger.exception("Échec rappel événement id=%s", event.pk)
    return sent
