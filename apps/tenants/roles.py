"""Rôles et matrice de permissions par cabinet."""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.TextChoices):
    """Rôles d'un membre au sein d'un cabinet."""

    OWNER = "owner", _("Propriétaire")
    LAWYER = "lawyer", _("Avocat")
    ASSOCIATE = "associate", _("Collaborateur")
    SECRETARY = "secretary", _("Secrétaire")
    READ_ONLY = "read_only", _("Lecture seule")


# Permissions logiques (pas Django auth perms)
PERM_VIEW = "view"
PERM_ADD = "add"
PERM_CHANGE = "change"
PERM_DELETE = "delete"
PERM_MANAGE_MEMBERS = "manage_members"
PERM_MANAGE_BILLING = "manage_billing"
PERM_MANAGE_CABINET = "manage_cabinet"
PERM_INVITE = "invite"

_ALL = frozenset(
    {
        PERM_VIEW,
        PERM_ADD,
        PERM_CHANGE,
        PERM_DELETE,
        PERM_MANAGE_MEMBERS,
        PERM_MANAGE_BILLING,
        PERM_MANAGE_CABINET,
        PERM_INVITE,
    }
)

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    Role.OWNER: _ALL,
    Role.LAWYER: frozenset({PERM_VIEW, PERM_ADD, PERM_CHANGE, PERM_DELETE, PERM_INVITE}),
    Role.ASSOCIATE: frozenset({PERM_VIEW, PERM_ADD, PERM_CHANGE}),
    Role.SECRETARY: frozenset({PERM_VIEW, PERM_ADD, PERM_CHANGE}),
    Role.READ_ONLY: frozenset({PERM_VIEW}),
}


def role_has_perm(role: str, perm: str) -> bool:
    """Indique si un rôle possède une permission logique."""
    return perm in ROLE_PERMISSIONS.get(role, frozenset())
