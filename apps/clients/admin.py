"""Admin clients (UI métier complète à l'étape 4)."""

from __future__ import annotations

from django.contrib import admin

from apps.clients.models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Administration des clients."""

    list_display = ("display_name", "client_type", "cabinet", "email", "updated_at")
    list_filter = ("client_type",)
    search_fields = ("first_name", "last_name", "company_name", "email")
    raw_id_fields = ("cabinet", "created_by")
