"""Vues cabinet : sélecteur, invitations."""

from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _g, gettext_lazy as _
from django.views import View
from django.views.generic import FormView, ListView

from apps.core.mixins import BreadcrumbMixin
from apps.tenants.forms import InviteMemberForm
from apps.tenants.mixins import CabinetPermissionMixin, CabinetRequiredMixin
from apps.tenants.models import Cabinet, Invitation
from apps.tenants.roles import PERM_INVITE
from apps.tenants.services import invite_member, switch_cabinet


class SwitchCabinetView(CabinetRequiredMixin, View):
    """Change le cabinet courant (POST)."""

    cabinet_required = False  # on peut switch même si session invalide
    http_method_names = ("post",)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Bascule vers le cabinet demandé."""
        cabinet_id = request.POST.get("cabinet_id", "")
        try:
            cabinet = switch_cabinet(
                request=request,
                user=request.user,  # type: ignore[arg-type]
                cabinet_id=cabinet_id,
            )
        except PermissionDenied:
            messages.error(request, _("Accès refusé à ce cabinet."))
            return redirect("core:home")
        except (Cabinet.DoesNotExist, ValidationError, ValueError):
            messages.error(request, _("Cabinet introuvable."))
            return redirect("core:home")

        messages.success(request, _("Cabinet actif : %(name)s") % {"name": cabinet.name})
        next_url = request.POST.get("next") or reverse("core:home")
        return HttpResponseRedirect(next_url)


class InviteMemberView(CabinetPermissionMixin, BreadcrumbMixin, FormView):
    """Invite un collaborateur dans le cabinet courant."""

    template_name = "tenants/invite_member.html"
    form_class = InviteMemberForm
    required_perm = PERM_INVITE
    success_url = "/app/"

    def get_breadcrumb(self) -> list[dict[str, str]]:
        """Fil d'Ariane invitation."""
        return [
            {"label": _g("Équipe"), "url": reverse("tenants:invitation_list")},
            {"label": _g("Inviter")},
        ]

    def get_success_url(self) -> str:
        """Redirige vers la liste des invitations."""
        return reverse("tenants:invitation_list")

    def form_valid(self, form: InviteMemberForm) -> HttpResponse:
        """Crée l'invitation et envoie l'e-mail."""
        cabinet = self.request.cabinet  # type: ignore[attr-defined]
        try:
            invitation = invite_member(
                cabinet=cabinet,
                email=form.cleaned_data["email"],
                role=form.cleaned_data["role"],
                invited_by=self.request.user,  # type: ignore[arg-type]
            )
        except (ValidationError, PermissionDenied) as exc:
            form.add_error(None, exc)
            return self.form_invalid(form)

        accept_url = self.request.build_absolute_uri(
            reverse("accounts:accept_invitation", kwargs={"token": invitation.token})
        )
        send_mail(
            subject=str(
                _("Invitation à rejoindre %(cabinet)s sur AvoLex") % {"cabinet": cabinet.name}
            ),
            message=str(
                _(
                    "Vous êtes invité(e) à rejoindre le cabinet %(cabinet)s sur AvoLex.\n\n"
                    "Accepter l'invitation : %(url)s\n\n"
                    "Cette invitation expire le %(expires)s."
                )
                % {
                    "cabinet": cabinet.name,
                    "url": accept_url,
                    "expires": invitation.expires_at.strftime("%d/%m/%Y %H:%M"),
                }
            ),
            from_email=None,
            recipient_list=[invitation.email],
            fail_silently=False,
        )
        messages.success(
            self.request, _("Invitation envoyée à %(email)s.") % {"email": invitation.email}
        )
        return super().form_valid(form)


class InvitationListView(CabinetPermissionMixin, BreadcrumbMixin, ListView):
    """Liste les invitations du cabinet courant."""

    template_name = "tenants/invitation_list.html"
    context_object_name = "invitations"
    paginate_by = 10
    required_perm = PERM_INVITE

    def get_breadcrumb(self) -> list[dict[str, str]]:
        """Fil d'Ariane liste invitations."""
        return [{"label": _g("Équipe & invitations")}]

    def get_queryset(self) -> Any:
        """Invitations du cabinet courant."""
        return (
            Invitation.objects.filter(cabinet=self.request.cabinet)  # type: ignore[attr-defined]
            .select_related("invited_by")
            .order_by("-created_at")
        )


__all__ = [
    "InvitationListView",
    "InviteMemberView",
    "SwitchCabinetView",
]
