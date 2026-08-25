"""Mixins de permission cabinet pour les CBV."""

from __future__ import annotations

from typing import Any, ClassVar

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _

from apps.tenants.roles import PERM_VIEW, role_has_perm
from apps.tenants.services import get_membership


class CabinetRequiredMixin(LoginRequiredMixin):
    """Exige un utilisateur authentifié et un cabinet courant."""

    cabinet_required: ClassVar[bool] = True

    def setup_cabinet_context(self, request: HttpRequest) -> None:
        """Assure ``request.membership`` à partir du cabinet courant."""
        cabinet = getattr(request, "cabinet", None)
        membership = getattr(request, "membership", None)
        if membership is None and cabinet is not None and request.user.is_authenticated:
            membership = get_membership(user=request.user, cabinet=cabinet)  # type: ignore[arg-type]
            request.membership = membership  # type: ignore[attr-defined]

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Vérifie auth + cabinet avant d'exécuter la vue."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        self.setup_cabinet_context(request)
        cabinet = getattr(request, "cabinet", None)
        membership = getattr(request, "membership", None)

        if self.cabinet_required and cabinet is None:
            raise PermissionDenied(_("Aucun cabinet sélectionné."))
        if self.cabinet_required and membership is None:
            raise PermissionDenied(_("Vous n'appartenez pas à ce cabinet."))

        return super().dispatch(request, *args, **kwargs)


class CabinetPermissionMixin(CabinetRequiredMixin):
    """Exige une permission logique (et optionnellement des rôles) sur le cabinet."""

    required_perm: ClassVar[str] = PERM_VIEW
    required_roles: ClassVar[tuple[str, ...]] = ()

    def check_cabinet_permission(self, request: HttpRequest) -> None:
        """Lève PermissionDenied si le rôle est insuffisant."""
        membership = getattr(request, "membership", None)
        if membership is None:
            raise PermissionDenied(_("Permission refusée."))

        if self.required_roles and membership.role not in self.required_roles:
            raise PermissionDenied(_("Rôle insuffisant pour cette action."))

        if self.required_perm and not role_has_perm(membership.role, self.required_perm):
            raise PermissionDenied(_("Permission insuffisante pour cette action."))

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Auth + cabinet + permission logique."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        self.setup_cabinet_context(request)
        cabinet = getattr(request, "cabinet", None)
        membership = getattr(request, "membership", None)

        if self.cabinet_required and cabinet is None:
            raise PermissionDenied(_("Aucun cabinet sélectionné."))
        if self.cabinet_required and membership is None:
            raise PermissionDenied(_("Vous n'appartenez pas à ce cabinet."))

        self.check_cabinet_permission(request)
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
