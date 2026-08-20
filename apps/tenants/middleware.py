"""Middleware de résolution du cabinet courant."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from apps.tenants.context import reset_current_cabinet, set_current_cabinet
from apps.tenants.services import resolve_cabinet_for_request

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse


class CabinetMiddleware:
    """
    Attache ``request.cabinet`` et alimente le ContextVar multi-tenant.

    Doit être placé après ``AuthenticationMiddleware``.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        cabinet = resolve_cabinet_for_request(request)
        request.cabinet = cabinet  # type: ignore[attr-defined]
        request.membership = None  # type: ignore[attr-defined]

        if cabinet is not None and request.user.is_authenticated:
            from apps.tenants.services import get_membership

            request.membership = get_membership(user=request.user, cabinet=cabinet)  # type: ignore[arg-type]

        token = set_current_cabinet(cabinet)
        try:
            return self.get_response(request)
        finally:
            reset_current_cabinet(token)
