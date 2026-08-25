"""Services agenda."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.calendar_app.models import Event, EventType
from apps.tenants.roles import PERM_ADD, PERM_CHANGE, PERM_DELETE
from apps.tenants.services import require_cabinet_perm

if TYPE_CHECKING:
    from apps.accounts.models import User
    from apps.matters.models import Matter
    from apps.tenants.models import Cabinet


def events_queryset(
    *,
    cabinet: Cabinet,
    from_dt: datetime | None = None,
    to_dt: datetime | None = None,
    event_type: str = "",
    matter_id: str = "",
) -> QuerySet[Event]:
    """Événements filtrés."""
    qs = Event.objects.filter(cabinet=cabinet).select_related("matter", "assigned_to")
    if from_dt:
        qs = qs.filter(starts_at__gte=from_dt)
    if to_dt:
        qs = qs.filter(starts_at__lte=to_dt)
    if event_type:
        qs = qs.filter(event_type=event_type)
    if matter_id:
        qs = qs.filter(matter_id=matter_id)
    return qs.order_by("starts_at")


@transaction.atomic
def create_event(
    *,
    cabinet: Cabinet,
    user: User,
    title: str,
    starts_at: datetime,
    event_type: str = EventType.APPOINTMENT,
    matter: Matter | None = None,
    description: str = "",
    ends_at: datetime | None = None,
    all_day: bool = False,
    location: str = "",
    assigned_to: User | None = None,
    remind_at: datetime | None = None,
) -> Event:
    """Crée un événement / tâche."""
    require_cabinet_perm(user=user, cabinet=cabinet, perm=PERM_ADD)
    if matter is not None and matter.cabinet_id != cabinet.pk:
        raise PermissionDenied(_("Dossier inaccessible."))
    if not title.strip():
        raise ValidationError({"title": _("Le titre est obligatoire.")})
    return Event.objects.create(
        cabinet=cabinet,
        created_by=user,
        matter=matter,
        event_type=event_type,
        title=title.strip(),
        description=description,
        starts_at=starts_at,
        ends_at=ends_at,
        all_day=all_day,
        location=location,
        assigned_to=assigned_to or user,
        remind_at=remind_at,
    )


@transaction.atomic
def update_event(*, event: Event, user: User, **fields: Any) -> Event:
    """Met à jour un événement."""
    require_cabinet_perm(user=user, cabinet=event.cabinet, perm=PERM_CHANGE)
    for key, value in fields.items():
        setattr(event, key, value)
    event.save()
    return event


@transaction.atomic
def mark_event_done(*, event: Event, user: User, done: bool = True) -> Event:
    """Marque une tâche comme terminée."""
    require_cabinet_perm(user=user, cabinet=event.cabinet, perm=PERM_CHANGE)
    event.is_done = done
    event.save(update_fields=["is_done", "updated_at"])
    return event


@transaction.atomic
def soft_delete_event(*, event: Event, user: User) -> None:
    """Suppression logique."""
    require_cabinet_perm(user=user, cabinet=event.cabinet, perm=PERM_DELETE)
    event.soft_delete()


def pending_reminders(*, now: datetime | None = None) -> QuerySet[Event]:
    """Événements dont le rappel est dû."""
    now = now or timezone.now()
    return Event.unscoped.filter(
        is_deleted=False,
        remind_at__isnull=False,
        remind_at__lte=now,
        reminder_sent_at__isnull=True,
    ).select_related("cabinet", "assigned_to", "matter")
