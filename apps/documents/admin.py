"""Admin Django pour la GED."""

from __future__ import annotations

from django.contrib import admin

from apps.documents.models import Document, DocumentVersion


class DocumentVersionInline(admin.TabularInline):
    """Versions en lecture dans l'admin document."""

    model = DocumentVersion
    extra = 0
    readonly_fields = (
        "version_number",
        "original_filename",
        "checksum",
        "size",
        "mime_type",
        "uploaded_by",
        "created_at",
    )
    can_delete = False


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Administration des documents."""

    list_display = ("title", "matter", "cabinet", "updated_at", "is_deleted")
    list_filter = ("is_deleted",)
    search_fields = ("title", "matter__reference", "matter__title")
    raw_id_fields = ("matter", "cabinet", "current_version", "created_by")
    inlines = [DocumentVersionInline]


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Administration des versions."""

    list_display = (
        "document",
        "version_number",
        "original_filename",
        "size",
        "mime_type",
        "created_at",
    )
    search_fields = ("original_filename", "checksum", "document__title")
    raw_id_fields = ("document", "cabinet", "uploaded_by", "created_by")
    readonly_fields = ("checksum", "size", "mime_type", "version_number")
