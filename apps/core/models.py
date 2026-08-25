"""Modèles abstraits partagés : BaseModel et TenantOwnedModel."""

from __future__ import annotations

import uuid
from typing import Any

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.managers import SoftDeleteManager, SoftDeleteQuerySet, TenantManager, TenantQuerySet


class BaseModel(models.Model):
    """Modèle de base : UUID, horodatage, auteur, soft-delete."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(_("créé le"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("modifié le"), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("créé par"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created",
    )
    is_deleted = models.BooleanField(_("supprimé"), default=False, db_index=True)
    deleted_at = models.DateTimeField(_("supprimé le"), null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
        ordering = ("-created_at",)

    def soft_delete(self, *, save: bool = True) -> None:
        """Marque l'instance comme soft-deleted."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if save:
            self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def restore(self, *, save: bool = True) -> None:
        """Annule un soft-delete."""
        self.is_deleted = False
        self.deleted_at = None
        if save:
            self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])


class TenantOwnedModel(BaseModel):
    """Modèle métier appartenant à un cabinet (isolation multi-tenant)."""

    cabinet = models.ForeignKey(
        "tenants.Cabinet",
        verbose_name=_("cabinet"),
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
    )

    objects = TenantManager()
    unscoped = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Assigne le cabinet courant si absent (création)."""
        if self.cabinet_id is None:
            from apps.tenants.context import get_current_cabinet

            current = get_current_cabinet()
            if current is not None:
                self.cabinet = current
        super().save(*args, **kwargs)


__all__ = [
    "BaseModel",
    "SoftDeleteManager",
    "SoftDeleteQuerySet",
    "TenantManager",
    "TenantOwnedModel",
    "TenantQuerySet",
]
