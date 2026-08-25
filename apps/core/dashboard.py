"""Agrégats du tableau de bord cabinet."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.billing.models import Invoice, InvoiceStatus, TimeEntry
from apps.calendar_app.models import Event
from apps.clients.models import Client
from apps.matters.models import Matter, MatterStatus

if TYPE_CHECKING:
    from apps.tenants.models import Cabinet


ACTIVE_MATTER_STATUSES = (
    MatterStatus.OPEN,
    MatterStatus.IN_PROGRESS,
    MatterStatus.ON_HOLD,
)

UNPAID_STATUSES = (InvoiceStatus.SENT, InvoiceStatus.OVERDUE)


@dataclass(frozen=True)
class DashboardStats:
    """KPIs simples du cabinet."""

    clients_count: int
    matters_active: int
    matters_total: int
    events_upcoming: int
    unbilled_hours_amount: Decimal
    unpaid_invoices: int
    revenue_month: Decimal


def build_dashboard_stats(*, cabinet: Cabinet) -> DashboardStats:
    """Calcule les indicateurs du dashboard pour un cabinet."""
    today = timezone.localdate()
    month_start = today.replace(day=1)
    now = timezone.now()

    clients_count = Client.objects.filter(cabinet=cabinet).count()
    matters_total = Matter.objects.filter(cabinet=cabinet, is_archived=False).count()
    matters_active = Matter.objects.filter(
        cabinet=cabinet,
        is_archived=False,
        status__in=ACTIVE_MATTER_STATUSES,
    ).count()
    events_upcoming = Event.objects.filter(
        cabinet=cabinet,
        starts_at__gte=now,
        is_done=False,
    ).count()

    unbilled_amount = Decimal("0.00")
    for entry in TimeEntry.objects.filter(
        cabinet=cabinet,
        is_billable=True,
        invoice__isnull=True,
        ended_at__isnull=False,
    ).only("duration_minutes", "hourly_rate")[:500]:
        unbilled_amount += entry.amount

    unpaid_invoices = Invoice.objects.filter(
        cabinet=cabinet,
        status__in=UNPAID_STATUSES,
    ).count()

    revenue = Invoice.objects.filter(
        cabinet=cabinet,
        status=InvoiceStatus.PAID,
        paid_at__gte=month_start,
    ).aggregate(total=Coalesce(Sum("total"), Decimal("0.00")))

    return DashboardStats(
        clients_count=clients_count,
        matters_active=matters_active,
        matters_total=matters_total,
        events_upcoming=events_upcoming,
        unbilled_hours_amount=unbilled_amount.quantize(Decimal("0.01")),
        unpaid_invoices=unpaid_invoices,
        revenue_month=Decimal(revenue["total"] or 0).quantize(Decimal("0.01")),
    )


def recent_matters(*, cabinet: Cabinet, limit: int = 5) -> list[Matter]:
    """Derniers dossiers mis à jour."""
    return list(
        Matter.objects.filter(cabinet=cabinet, is_archived=False)
        .select_related("client")
        .order_by("-updated_at")[:limit]
    )


def upcoming_events(*, cabinet: Cabinet, limit: int = 5) -> list[Event]:
    """Prochains événements."""
    return list(
        Event.objects.filter(cabinet=cabinet, starts_at__gte=timezone.now())
        .select_related("matter")
        .order_by("starts_at")[:limit]
    )
