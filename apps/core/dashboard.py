"""Agrégats du tableau de bord cabinet."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.billing.models import Invoice, InvoiceStatus, TimeEntry
from apps.calendar_app.models import Event, EventType, HearingStatus
from apps.clients.models import Client
from apps.matters.models import Matter, MatterStatus
from apps.tenants.models import Cabinet, Membership

if TYPE_CHECKING:
    pass


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
    hearings_upcoming: int
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
    hearings_upcoming = Event.objects.filter(
        cabinet=cabinet,
        event_type=EventType.HEARING,
        starts_at__gte=now,
        hearing_status__in=(HearingStatus.SCHEDULED, ""),
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
        hearings_upcoming=hearings_upcoming,
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


def upcoming_hearings(*, cabinet: Cabinet, limit: int = 5) -> list[Event]:
    """Prochaines audiences planifiées."""
    return list(
        Event.objects.filter(
            cabinet=cabinet,
            event_type=EventType.HEARING,
            starts_at__gte=timezone.now(),
            hearing_status__in=(HearingStatus.SCHEDULED, ""),
        )
        .select_related("matter", "matter__client")
        .order_by("starts_at")[:limit]
    )


def upcoming_events(*, cabinet: Cabinet, limit: int = 5) -> list[Event]:
    """Prochains événements."""
    return list(
        Event.objects.filter(cabinet=cabinet, starts_at__gte=timezone.now())
        .select_related("matter")
        .order_by("starts_at")[:limit]
    )


@dataclass(frozen=True)
class CabinetOverview:
    """Résumé d'activité d'un cabinet (supervision plateforme)."""

    cabinet: Cabinet
    members_count: int
    clients_count: int
    matters_active: int
    hearings_upcoming: int
    unpaid_invoices: int


@dataclass(frozen=True)
class PlatformStats:
    """Totaux globaux plateforme."""

    cabinets_count: int
    members_count: int
    clients_count: int
    matters_active: int
    hearings_upcoming: int
    unpaid_invoices: int


def build_platform_stats() -> PlatformStats:
    """Agrégats cross-cabinet pour l'administrateur plateforme."""
    now = timezone.now()
    cabinets_count = Cabinet.objects.filter(is_active=True).count()
    members_count = Membership.objects.filter(is_active=True).count()
    clients_count = Client.unscoped.count()
    matters_active = Matter.unscoped.filter(
        is_archived=False,
        status__in=ACTIVE_MATTER_STATUSES,
    ).count()
    hearings_upcoming = Event.unscoped.filter(
        event_type=EventType.HEARING,
        starts_at__gte=now,
        hearing_status__in=(HearingStatus.SCHEDULED, ""),
    ).count()
    unpaid_invoices = Invoice.unscoped.filter(status__in=UNPAID_STATUSES).count()
    return PlatformStats(
        cabinets_count=cabinets_count,
        members_count=members_count,
        clients_count=clients_count,
        matters_active=matters_active,
        hearings_upcoming=hearings_upcoming,
        unpaid_invoices=unpaid_invoices,
    )


def list_cabinet_overviews(*, limit: int = 50) -> list[CabinetOverview]:
    """Liste les cabinets avec indicateurs d'activité."""
    now = timezone.now()
    cabinets = list(Cabinet.objects.filter(is_active=True).order_by("name")[:limit])
    overviews: list[CabinetOverview] = []
    for cabinet in cabinets:
        overviews.append(
            CabinetOverview(
                cabinet=cabinet,
                members_count=Membership.objects.filter(
                    cabinet=cabinet, is_active=True
                ).count(),
                clients_count=Client.unscoped.filter(cabinet=cabinet).count(),
                matters_active=Matter.unscoped.filter(
                    cabinet=cabinet,
                    is_archived=False,
                    status__in=ACTIVE_MATTER_STATUSES,
                ).count(),
                hearings_upcoming=Event.unscoped.filter(
                    cabinet=cabinet,
                    event_type=EventType.HEARING,
                    starts_at__gte=now,
                    hearing_status__in=(HearingStatus.SCHEDULED, ""),
                ).count(),
                unpaid_invoices=Invoice.unscoped.filter(
                    cabinet=cabinet,
                    status__in=UNPAID_STATUSES,
                ).count(),
            )
        )
    return overviews


def recent_platform_activity(*, limit: int = 12) -> list[Matter]:
    """Derniers dossiers mis à jour, tous cabinets confondus."""
    return list(
        Matter.unscoped.filter(is_archived=False)
        .select_related("cabinet", "client")
        .order_by("-updated_at")[:limit]
    )


def upcoming_platform_hearings(*, limit: int = 10) -> list[Event]:
    """Prochaines audiences, tous cabinets confondus."""
    return list(
        Event.unscoped.filter(
            event_type=EventType.HEARING,
            starts_at__gte=timezone.now(),
            hearing_status__in=(HearingStatus.SCHEDULED, ""),
        )
        .select_related("cabinet", "matter", "matter__client")
        .order_by("starts_at")[:limit]
    )
