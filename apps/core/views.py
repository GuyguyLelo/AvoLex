"""Vues transverses (landing, healthcheck, home)."""

from __future__ import annotations

from typing import Any

from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import TemplateView

from apps.core.dashboard import build_dashboard_stats, recent_matters, upcoming_events
from apps.core.mixins import BreadcrumbMixin
from apps.tenants.mixins import CabinetRequiredMixin


class LandingView(TemplateView):
    """Page marketing publique. Les utilisateurs déjà connectés vont à l'app."""

    template_name = "core/landing.html"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Évite de redemander une connexion si la session est déjà active."""
        if request.user.is_authenticated:
            return redirect("core:home")
        return super().dispatch(request, *args, **kwargs)


class HomeView(CabinetRequiredMixin, BreadcrumbMixin, TemplateView):
    """Tableau de bord avec KPIs."""

    template_name = "core/home.html"

    def get_breadcrumb(self) -> list[dict[str, str]]:
        """Pas de fil d'Ariane : le bandeau du dashboard suffit."""
        return []

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Ajoute les statistiques du cabinet courant."""
        ctx = super().get_context_data(**kwargs)
        cabinet = self.request.cabinet  # type: ignore[attr-defined]
        ctx["stats"] = build_dashboard_stats(cabinet=cabinet)
        ctx["recent_matters"] = recent_matters(cabinet=cabinet)
        ctx["upcoming_events"] = upcoming_events(cabinet=cabinet)
        return ctx


class HealthCheckView(View):
    """Endpoint de santé pour reverse-proxy / monitoring."""

    http_method_names = ("get", "head")

    def get(self, request: HttpRequest) -> HttpResponse:
        """Vérifie la connexion PostgreSQL et renvoie un JSON de statut."""
        db_ok = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_ok = cursor.fetchone() is not None
        except Exception:
            db_ok = False

        status = 200 if db_ok else 503
        payload = {
            "status": "ok" if db_ok else "degraded",
            "database": "up" if db_ok else "down",
            "service": "avolex",
        }
        return JsonResponse(payload, status=status)
