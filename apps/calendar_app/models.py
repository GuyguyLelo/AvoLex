"""Modèles agenda : événements et tâches."""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TenantOwnedModel


class EventType(models.TextChoices):
    """Type d'événement agenda."""

    HEARING = "hearing", _("Audience")
    APPOINTMENT = "appointment", _("Rendez-vous")
    DEADLINE = "deadline", _("Délai de procédure")
    REMINDER = "reminder", _("Rappel")
    TASK = "task", _("Tâche")


class Event(TenantOwnedModel):
    """Événement / échéance / tâche du cabinet."""

    matter = models.ForeignKey(
        "matters.Matter",
        verbose_name=_("dossier"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )
    event_type = models.CharField(
        _("type"),
        max_length=20,
        choices=EventType.choices,
        default=EventType.APPOINTMENT,
        db_index=True,
    )
    title = models.CharField(_("titre"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    starts_at = models.DateTimeField(_("début"), db_index=True)
    ends_at = models.DateTimeField(_("fin"), null=True, blank=True)
    all_day = models.BooleanField(_("journée entière"), default=False)
    location = models.CharField(_("lieu"), max_length=255, blank=True)
    is_done = models.BooleanField(_("terminé"), default=False)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("assigné à"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_events",
    )
    remind_at = models.DateTimeField(
        _("rappel le"),
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Date/heure d'envoi du rappel e-mail."),
    )
    reminder_sent_at = models.DateTimeField(_("rappel envoyé le"), null=True, blank=True)

    class Meta:
        verbose_name = _("événement")
        verbose_name_plural = _("événements")
        ordering = ("starts_at",)
        indexes = [
            models.Index(fields=["cabinet", "starts_at"], name="calendar_ap_cabinet_7be077_idx"),
            models.Index(
                fields=["cabinet", "event_type", "starts_at"],
                name="calendar_ap_cabinet_6708af_idx",
            ),
            models.Index(
                fields=["remind_at"],
                name="cal_event_remind_pending_idx",
                condition=models.Q(is_deleted=False, reminder_sent_at__isnull=True),
            ),
        ]

    def __str__(self) -> str:
        return self.title
