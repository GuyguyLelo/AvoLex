"""Vues agenda."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _g
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.calendar_app.forms import EventForm
from apps.calendar_app.models import Event, EventType
from apps.calendar_app.services import (
    create_event,
    events_queryset,
    mark_event_done,
    soft_delete_event,
    update_event,
)
from apps.core.mixins import BreadcrumbMixin
from apps.matters.models import Matter
from apps.tenants.mixins import CabinetPermissionMixin
from apps.tenants.roles import PERM_ADD, PERM_CHANGE, PERM_DELETE, PERM_VIEW


class CalendarListView(CabinetPermissionMixin, BreadcrumbMixin, ListView):
    """Agenda : 30 jours à venir + tâches."""

    template_name = "calendar_app/event_list.html"
    context_object_name = "events"
    paginate_by = 10
    required_perm = PERM_VIEW

    def get_breadcrumb(self) -> list[dict[str, str]]:
        return [{"label": _g("Agenda")}]

    def get_queryset(self) -> QuerySet[Event]:
        now = timezone.now()
        return events_queryset(
            cabinet=self.request.cabinet,  # type: ignore[attr-defined]
            from_dt=now - timedelta(days=1),
            to_dt=now + timedelta(days=60),
            event_type=self.request.GET.get("type", ""),
            matter_id=self.request.GET.get("matter", ""),
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["event_types"] = EventType.choices
        ctx["filter_type"] = self.request.GET.get("type", "")
        ctx["filter_matter"] = self.request.GET.get("matter", "")
        ctx["matters"] = Matter.objects.order_by("reference")
        ctx["open_tasks"] = Event.objects.filter(
            event_type=EventType.TASK,
            is_done=False,
        ).order_by("starts_at")[:20]
        return ctx


class EventDetailView(CabinetPermissionMixin, BreadcrumbMixin, DetailView):
    """Fiche événement / tâche."""

    template_name = "calendar_app/event_detail.html"
    context_object_name = "event"
    required_perm = PERM_VIEW

    def get_queryset(self) -> QuerySet[Event]:
        return Event.objects.select_related(
            "matter",
            "matter__client",
            "assigned_to",
            "created_by",
        )

    def get_breadcrumb(self) -> list[dict[str, str]]:
        return [
            {"label": _g("Agenda"), "url": reverse("calendar:list")},
            {"label": self.object.title},
        ]


class EventCreateView(CabinetPermissionMixin, BreadcrumbMixin, CreateView):
    """Création événement / tâche."""

    template_name = "calendar_app/event_form.html"
    form_class = EventForm
    required_perm = PERM_ADD

    def get_breadcrumb(self) -> list[dict[str, str]]:
        return [
            {"label": _g("Agenda"), "url": reverse("calendar:list")},
            {"label": _g("Nouvel événement")},
        ]

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["matter_queryset"] = Matter.objects.order_by("reference")
        return kwargs

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        matter_id = self.request.GET.get("matter")
        if matter_id:
            initial["matter"] = matter_id
        if self.request.GET.get("type") == EventType.TASK:
            initial["event_type"] = EventType.TASK
        return initial

    def form_valid(self, form: EventForm) -> HttpResponse:
        data = form.cleaned_data
        try:
            event = create_event(
                cabinet=self.request.cabinet,  # type: ignore[attr-defined]
                user=self.request.user,  # type: ignore[arg-type]
                title=data["title"],
                starts_at=data["starts_at"],
                event_type=data.get("event_type") or EventType.APPOINTMENT,
                matter=data.get("matter"),
                description=data.get("description") or "",
                ends_at=data.get("ends_at"),
                all_day=data.get("all_day") or False,
                location=data.get("location") or "",
                remind_at=data.get("remind_at"),
            )
        except (ValidationError, PermissionDenied) as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, _g("Événement créé."))
        return redirect("calendar:event_detail", pk=event.pk)


class EventUpdateView(CabinetPermissionMixin, BreadcrumbMixin, UpdateView):
    """Édition."""

    template_name = "calendar_app/event_form.html"
    form_class = EventForm
    context_object_name = "event"
    required_perm = PERM_CHANGE

    def get_queryset(self) -> QuerySet[Event]:
        return Event.objects.all()

    def get_breadcrumb(self) -> list[dict[str, str]]:
        return [
            {"label": _g("Agenda"), "url": reverse("calendar:list")},
            {"label": self.object.title, "url": reverse("calendar:event_detail", kwargs={"pk": self.object.pk})},
            {"label": _g("Modifier")},
        ]

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["matter_queryset"] = Matter.objects.order_by("reference")
        return kwargs

    def form_valid(self, form: EventForm) -> HttpResponse:
        try:
            update_event(
                event=self.object,
                user=self.request.user,  # type: ignore[arg-type]
                **form.cleaned_data,
            )
        except (ValidationError, PermissionDenied) as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, _g("Événement mis à jour."))
        return redirect("calendar:event_detail", pk=self.object.pk)


class EventDoneView(CabinetPermissionMixin, View):
    """Marquer tâche terminée."""

    required_perm = PERM_CHANGE
    http_method_names = ("post",)

    def post(self, request: Any, pk: str) -> HttpResponse:
        event = get_object_or_404(Event, pk=pk)
        mark_event_done(event=event, user=request.user, done=True)
        messages.success(request, _g("Tâche terminée."))
        return redirect("calendar:event_detail", pk=event.pk)


class EventDeleteView(CabinetPermissionMixin, View):
    """Suppression."""

    required_perm = PERM_DELETE
    http_method_names = ("post",)

    def post(self, request: Any, pk: str) -> HttpResponse:
        event = get_object_or_404(Event, pk=pk)
        soft_delete_event(event=event, user=request.user)
        messages.success(request, _g("Événement supprimé."))
        return redirect("calendar:list")
