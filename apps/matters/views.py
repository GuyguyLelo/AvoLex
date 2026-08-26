"""Vues CRUD dossiers."""

from __future__ import annotations

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

from apps.clients.models import Client
from apps.core.mixins import BreadcrumbMixin
from apps.matters.forms import MatterForm
from apps.calendar_app.models import Event, EventType, HearingStatus
from apps.matters.models import Matter, MatterStatus
from apps.matters.services import archive_matter, create_matter, matters_queryset, soft_delete_matter, update_matter
from apps.tenants.mixins import CabinetPermissionMixin
from apps.tenants.models import Membership
from apps.tenants.roles import PERM_ADD, PERM_CHANGE, PERM_DELETE, PERM_VIEW, Role


class MatterListView(CabinetPermissionMixin, BreadcrumbMixin, ListView):
    """Liste paginée + filtres."""

    template_name = "matters/matter_list.html"
    context_object_name = "matters"
    paginate_by = 10
    required_perm = PERM_VIEW

    def get_breadcrumb(self) -> list[dict[str, str]]:
        return [{"label": _g("Dossiers")}]

    def get_queryset(self) -> QuerySet[Matter]:
        return matters_queryset(
            cabinet=self.request.cabinet,  # type: ignore[attr-defined]
            q=self.request.GET.get("q", ""),
            status=self.request.GET.get("status", ""),
            client_id=self.request.GET.get("client", ""),
            archived=self.request.GET.get("archived", ""),
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["filter_q"] = self.request.GET.get("q", "")
        ctx["filter_status"] = self.request.GET.get("status", "")
        ctx["filter_client"] = self.request.GET.get("client", "")
        ctx["filter_archived"] = self.request.GET.get("archived", "")
        ctx["status_choices"] = MatterStatus.choices
        ctx["clients"] = Client.objects.order_by("last_name", "company_name")
        return ctx


class MatterDetailView(CabinetPermissionMixin, BreadcrumbMixin, DetailView):
    """Fiche dossier + historique d'actions."""

    template_name = "matters/matter_detail.html"
    context_object_name = "matter"
    required_perm = PERM_VIEW

    def get_queryset(self) -> QuerySet[Matter]:
        return Matter.objects.select_related("client", "responsible_lawyer")

    def get_breadcrumb(self) -> list[dict[str, str]]:
        return [
            {"label": _g("Dossiers"), "url": reverse("matters:list")},
            {"label": self.object.reference},
        ]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["actions"] = self.object.actions.select_related("actor").all()[:50]
        matter: Matter = self.object
        ctx["can_delete_matter"] = not matter.is_treated
        ctx["can_archive_matter"] = (
            matter.status == MatterStatus.CLOSED and not matter.is_archived
        )
        now = timezone.now()
        ctx["upcoming_hearings"] = (
            matter.events.filter(
                event_type=EventType.HEARING,
                starts_at__gte=now,
                hearing_status__in=(HearingStatus.SCHEDULED, ""),
            )
            .select_related("assigned_to")
            .order_by("starts_at")[:10]
        )
        return ctx


def _lawyer_queryset(cabinet: Any) -> QuerySet[Any]:
    user_ids = Membership.objects.filter(
        cabinet=cabinet,
        is_active=True,
        role__in=(Role.OWNER, Role.LAWYER, Role.ASSOCIATE),
    ).values_list("user_id", flat=True)
    from django.contrib.auth import get_user_model

    return get_user_model().objects.filter(pk__in=user_ids).order_by("last_name", "email")


class MatterCreateView(CabinetPermissionMixin, BreadcrumbMixin, CreateView):
    """Création dossier."""

    template_name = "matters/matter_form.html"
    form_class = MatterForm
    required_perm = PERM_ADD

    def get_breadcrumb(self) -> list[dict[str, str]]:
        return [
            {"label": _g("Dossiers"), "url": reverse("matters:list")},
            {"label": _g("Nouveau dossier")},
        ]

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        cabinet = self.request.cabinet  # type: ignore[attr-defined]
        kwargs["client_queryset"] = Client.objects.order_by("last_name", "company_name")
        kwargs["lawyer_queryset"] = _lawyer_queryset(cabinet)
        return kwargs

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        client_id = self.request.GET.get("client")
        if client_id:
            initial["client"] = client_id
        initial["responsible_lawyer"] = self.request.user.pk
        return initial

    def form_valid(self, form: MatterForm) -> HttpResponse:
        data = form.cleaned_data
        try:
            matter = create_matter(
                cabinet=self.request.cabinet,  # type: ignore[attr-defined]
                user=self.request.user,  # type: ignore[arg-type]
                client=data["client"],
                title=data["title"],
                responsible_lawyer=data["responsible_lawyer"],
                description=data.get("description") or "",
                practice_area=data.get("practice_area") or "",
                jurisdiction=data.get("jurisdiction") or "",
                opposing_party=data.get("opposing_party") or "",
                status=data.get("status") or MatterStatus.OPEN,
                opened_at=data.get("opened_at"),
                closed_at=data.get("closed_at"),
                notes=data.get("notes") or "",
            )
        except (ValidationError, PermissionDenied) as exc:
            if isinstance(exc, ValidationError) and hasattr(exc, "message_dict"):
                for field, errs in exc.message_dict.items():
                    for err in errs:
                        form.add_error(field if field != "__all__" else None, err)
                return self.form_invalid(form)
            messages.error(self.request, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, _g("Dossier créé."))
        return redirect("matters:detail", pk=matter.pk)


class MatterUpdateView(CabinetPermissionMixin, BreadcrumbMixin, UpdateView):
    """Édition dossier."""

    template_name = "matters/matter_form.html"
    form_class = MatterForm
    context_object_name = "matter"
    required_perm = PERM_CHANGE

    def get_queryset(self) -> QuerySet[Matter]:
        return Matter.objects.all()

    def get_breadcrumb(self) -> list[dict[str, str]]:
        return [
            {"label": _g("Dossiers"), "url": reverse("matters:list")},
            {
                "label": self.object.reference,
                "url": reverse("matters:detail", args=[self.object.pk]),
            },
            {"label": _g("Modifier")},
        ]

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        cabinet = self.request.cabinet  # type: ignore[attr-defined]
        kwargs["client_queryset"] = Client.objects.order_by("last_name", "company_name")
        kwargs["lawyer_queryset"] = _lawyer_queryset(cabinet)
        return kwargs

    def form_valid(self, form: MatterForm) -> HttpResponse:
        try:
            update_matter(
                matter=self.object,
                user=self.request.user,  # type: ignore[arg-type]
                **form.cleaned_data,
            )
        except (ValidationError, PermissionDenied) as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, _g("Dossier mis à jour."))
        return redirect("matters:detail", pk=self.object.pk)


class MatterDeleteView(CabinetPermissionMixin, View):
    """Suppression logique."""

    required_perm = PERM_DELETE
    http_method_names = ("post",)

    def post(self, request: Any, pk: str) -> HttpResponse:
        matter = get_object_or_404(Matter, pk=pk)
        try:
            soft_delete_matter(matter=matter, user=request.user)
        except (ValidationError, PermissionDenied) as exc:
            messages.error(request, str(exc))
            return redirect("matters:detail", pk=pk)
        messages.success(request, _g("Dossier supprimé."))
        return redirect("matters:list")


class MatterArchiveView(CabinetPermissionMixin, View):
    """Archive un dossier clos."""

    required_perm = PERM_CHANGE
    http_method_names = ("post",)

    def post(self, request: Any, pk: str) -> HttpResponse:
        matter = get_object_or_404(Matter, pk=pk)
        try:
            archive_matter(matter=matter, user=request.user)
        except (ValidationError, PermissionDenied) as exc:
            messages.error(request, str(exc))
            return redirect("matters:detail", pk=pk)
        messages.success(request, _g("Dossier archivé."))
        return redirect("matters:detail", pk=pk)
