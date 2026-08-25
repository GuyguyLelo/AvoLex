"""Admin Django pour les modèles tenants."""

from __future__ import annotations

from django.contrib import admin

from apps.tenants.models import Cabinet, CabinetPreference, Invitation, Membership


@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    """Administration des cabinets."""

    list_display = ("name", "slug", "city", "is_active", "created_at")
    search_fields = ("name", "slug", "siret", "legal_name")
    list_filter = ("is_active", "country")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    """Administration des adhésions."""

    list_display = ("user", "cabinet", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("user__email", "cabinet__name")
    raw_id_fields = ("user", "cabinet", "created_by")


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """Administration des invitations."""

    list_display = ("email", "cabinet", "role", "expires_at", "accepted_at", "created_at")
    list_filter = ("role",)
    search_fields = ("email", "cabinet__name", "token")
    readonly_fields = ("token", "accepted_at")
    raw_id_fields = ("cabinet", "invited_by", "created_by")


@admin.register(CabinetPreference)
class CabinetPreferenceAdmin(admin.ModelAdmin):
    """Administration des préférences cabinet."""

    list_display = ("key", "cabinet", "updated_at")
    search_fields = ("key", "cabinet__name")
    raw_id_fields = ("cabinet", "created_by")
