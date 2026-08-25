"""Admin agenda."""

from __future__ import annotations

from django.contrib import admin

from apps.calendar_app.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Administration des événements."""

    list_display = ("title", "event_type", "starts_at", "cabinet", "is_done", "assigned_to")
    list_filter = ("event_type", "is_done")
    search_fields = ("title", "location")
    raw_id_fields = ("cabinet", "matter", "assigned_to", "created_by")
