"""Modèles multi-tenant : Cabinet, Membership, Invitation."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Any

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from apps.core.models import BaseModel, TenantOwnedModel
from apps.core.money import default_currency
from apps.tenants.roles import Role


def default_invitation_expiry() -> datetime:
    """Expiration par défaut d'une invitation (7 jours)."""
    return timezone.now() + timedelta(days=7)


def generate_invitation_token() -> str:
    """Génère un token d'invitation URL-safe."""
    return secrets.token_urlsafe(32)


class Cabinet(BaseModel):
    """Organisation / cabinet d'avocats (tenant)."""

    name = models.CharField(_("nom"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    legal_name = models.CharField(_("raison sociale"), max_length=255, blank=True)
    siret = models.CharField(_("SIRET"), max_length=14, blank=True)
    vat_number = models.CharField(_("n° TVA"), max_length=32, blank=True)
    bar_association = models.CharField(_("barreau"), max_length=255, blank=True)
    address_line1 = models.CharField(_("adresse"), max_length=255, blank=True)
    address_line2 = models.CharField(_("complément d'adresse"), max_length=255, blank=True)
    postal_code = models.CharField(_("code postal"), max_length=20, blank=True)
    city = models.CharField(_("ville"), max_length=100, blank=True)
    country = models.CharField(_("pays"), max_length=2, default="FR")
    default_currency = models.CharField(_("devise"), max_length=3, default=default_currency)
    retention_days = models.PositiveIntegerField(
        _("durée de conservation (jours)"),
        default=3650,
        help_text=_("Durée RGPD de conservation des données (par défaut 10 ans)."),
    )
    is_active = models.BooleanField(_("actif"), default=True)

    class Meta:
        verbose_name = _("cabinet")
        verbose_name_plural = _("cabinets")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Génère un slug unique si absent."""
        if not self.slug:
            base = slugify(self.name) or "cabinet"
            slug = base
            counter = 1
            while Cabinet.all_objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Membership(BaseModel):
    """Lien utilisateur ↔ cabinet avec un rôle."""

    cabinet = models.ForeignKey(
        Cabinet,
        verbose_name=_("cabinet"),
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("utilisateur"),
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(
        _("rôle"),
        max_length=32,
        choices=Role.choices,
        default=Role.READ_ONLY,
    )
    is_active = models.BooleanField(_("actif"), default=True)

    class Meta:
        verbose_name = _("adhésion")
        verbose_name_plural = _("adhésions")
        constraints = [
            models.UniqueConstraint(
                fields=("cabinet", "user"),
                condition=models.Q(is_deleted=False),
                name="uniq_active_membership_cabinet_user",
            ),
        ]
        indexes = [
            models.Index(fields=("user", "is_active")),
            models.Index(fields=("cabinet", "role")),
        ]

    def __str__(self) -> str:
        return f"{self.user} @ {self.cabinet} ({self.get_role_display()})"


class Invitation(BaseModel):
    """Invitation d'un collaborateur dans un cabinet."""

    cabinet = models.ForeignKey(
        Cabinet,
        verbose_name=_("cabinet"),
        on_delete=models.CASCADE,
        related_name="invitations",
    )
    email = models.EmailField(_("e-mail invité"), db_index=True)
    role = models.CharField(
        _("rôle"),
        max_length=32,
        choices=Role.choices,
        default=Role.ASSOCIATE,
    )
    token = models.CharField(
        _("jeton"),
        max_length=64,
        unique=True,
        default=generate_invitation_token,
        editable=False,
    )
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("invité par"),
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_invitations",
    )
    expires_at = models.DateTimeField(_("expire le"), default=default_invitation_expiry)
    accepted_at = models.DateTimeField(_("acceptée le"), null=True, blank=True)

    class Meta:
        verbose_name = _("invitation")
        verbose_name_plural = _("invitations")
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.email} → {self.cabinet}"

    @property
    def is_expired(self) -> bool:
        """True si l'invitation a dépassé sa date d'expiration."""
        return timezone.now() >= self.expires_at

    @property
    def is_accepted(self) -> bool:
        """True si l'invitation a déjà été acceptée."""
        return self.accepted_at is not None

    @property
    def is_pending(self) -> bool:
        """True si l'invitation est encore utilisable."""
        return not self.is_accepted and not self.is_expired and not self.is_deleted


class CabinetPreference(TenantOwnedModel):
    """Préférence clé/valeur par cabinet (et canari d'isolation multi-tenant)."""

    key = models.CharField(_("clé"), max_length=100)
    value = models.JSONField(_("valeur"), default=dict, blank=True)

    class Meta:
        verbose_name = _("préférence cabinet")
        verbose_name_plural = _("préférences cabinet")
        constraints = [
            models.UniqueConstraint(
                fields=("cabinet", "key"),
                condition=models.Q(is_deleted=False),
                name="uniq_cabinet_preference_key",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.cabinet.slug}:{self.key}"
