"""Services métier multi-tenant (pas de logique dans les vues)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.tenants.models import Cabinet, Invitation, Membership
from apps.tenants.roles import (
    PERM_INVITE,
    PERM_MANAGE_CABINET,
    PERM_MANAGE_MEMBERS,
    PERM_VIEW,
    Role,
    role_has_perm,
)

if TYPE_CHECKING:
    from django.http import HttpRequest

    from apps.accounts.models import User

logger = logging.getLogger(__name__)
UserModel = get_user_model()

SESSION_CABINET_KEY = "cabinet_id"


def get_membership(*, user: User, cabinet: Cabinet) -> Membership | None:
    """Retourne l'adhésion active d'un utilisateur pour un cabinet."""
    return (
        Membership.objects.select_related("cabinet", "user")
        .filter(user=user, cabinet=cabinet, is_active=True)
        .first()
    )


def user_has_cabinet_perm(*, user: User, cabinet: Cabinet, perm: str) -> bool:
    """Vérifie qu'un utilisateur a une permission logique sur un cabinet."""
    membership = get_membership(user=user, cabinet=cabinet)
    if membership is None:
        return False
    return role_has_perm(membership.role, perm)


def require_cabinet_perm(*, user: User, cabinet: Cabinet, perm: str) -> Membership:
    """Comme user_has_cabinet_perm mais lève PermissionDenied."""
    membership = get_membership(user=user, cabinet=cabinet)
    if membership is None or not role_has_perm(membership.role, perm):
        raise PermissionDenied(_("Permission refusée pour ce cabinet."))
    return membership


def list_user_cabinets(user: User) -> list[Cabinet]:
    """Liste les cabinets actifs auxquels l'utilisateur appartient."""
    return list(
        Cabinet.objects.filter(
            memberships__user=user,
            memberships__is_active=True,
            memberships__is_deleted=False,
            is_active=True,
        )
        .distinct()
        .order_by("name")
    )


@transaction.atomic
def create_cabinet_with_owner(
    *,
    owner: User,
    name: str,
    **extra_fields: object,
) -> tuple[Cabinet, Membership]:
    """
    Crée un cabinet et y rattache l'utilisateur comme Owner.

    Returns:
        Couple (cabinet, membership).
    """
    cabinet = Cabinet(name=name, created_by=owner, **extra_fields)  # type: ignore[arg-type]
    cabinet.save()
    membership = Membership.objects.create(
        cabinet=cabinet,
        user=owner,
        role=Role.OWNER,
        created_by=owner,
    )
    logger.info("Cabinet créé id=%s owner=%s", cabinet.pk, owner.pk)
    return cabinet, membership


@transaction.atomic
def register_user_with_cabinet(
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    cabinet_name: str,
) -> tuple[User, Cabinet, Membership]:
    """Inscription : crée l'utilisateur, le cabinet et l'adhésion Owner."""
    if UserModel.objects.filter(email__iexact=email).exists():
        raise ValidationError({"email": _("Un compte existe déjà avec cet e-mail.")})
    user = UserModel.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    cabinet, membership = create_cabinet_with_owner(owner=user, name=cabinet_name)
    return user, cabinet, membership


def set_session_cabinet(request: HttpRequest, cabinet: Cabinet) -> None:
    """Enregistre le cabinet courant en session."""
    request.session[SESSION_CABINET_KEY] = str(cabinet.pk)


def clear_session_cabinet(request: HttpRequest) -> None:
    """Retire le cabinet de la session."""
    request.session.pop(SESSION_CABINET_KEY, None)


def switch_cabinet(*, request: HttpRequest, user: User, cabinet_id: str) -> Cabinet:
    """
    Change le cabinet courant si l'utilisateur y a une adhésion active.

    Raises:
        PermissionDenied: si aucune adhésion active.
        Cabinet.DoesNotExist: si le cabinet est introuvable.
    """
    cabinet = Cabinet.objects.get(pk=cabinet_id, is_active=True)
    membership = get_membership(user=user, cabinet=cabinet)
    if membership is None:
        raise PermissionDenied(_("Vous n'appartenez pas à ce cabinet."))
    set_session_cabinet(request, cabinet)
    return cabinet


@transaction.atomic
def invite_member(
    *,
    cabinet: Cabinet,
    email: str,
    role: str,
    invited_by: User,
) -> Invitation:
    """Crée (ou renouvelle) une invitation pour un e-mail."""
    require_cabinet_perm(user=invited_by, cabinet=cabinet, perm=PERM_INVITE)

    if role == Role.OWNER:
        raise ValidationError(_("Impossible d'inviter un second propriétaire via invitation."))

    if not role_has_perm(role, PERM_VIEW):
        raise ValidationError({"role": _("Rôle invalide.")})

    email_norm = email.strip().lower()
    existing_user = UserModel.objects.filter(email__iexact=email_norm).first()
    if existing_user and get_membership(user=existing_user, cabinet=cabinet):
        raise ValidationError(_("Cet utilisateur est déjà membre du cabinet."))

    Invitation.objects.filter(
        cabinet=cabinet,
        email__iexact=email_norm,
        accepted_at__isnull=True,
        is_deleted=False,
    ).update(is_deleted=True, deleted_at=timezone.now())

    invitation = Invitation.objects.create(
        cabinet=cabinet,
        email=email_norm,
        role=role,
        invited_by=invited_by,
        created_by=invited_by,
    )
    logger.info(
        "Invitation créée cabinet=%s email=%s role=%s",
        cabinet.pk,
        email_norm,
        role,
    )
    return invitation


@transaction.atomic
def accept_invitation(
    *,
    token: str,
    user: User | None = None,
    password: str | None = None,
    first_name: str = "",
    last_name: str = "",
) -> tuple[User, Membership, Invitation]:
    """
    Accepte une invitation.

    Si ``user`` est None, crée un compte avec ``password``.
    """
    try:
        invitation = Invitation.objects.select_related("cabinet").get(
            token=token,
            is_deleted=False,
        )
    except Invitation.DoesNotExist as exc:
        raise ValidationError(_("Invitation introuvable.")) from exc

    if invitation.is_accepted:
        raise ValidationError(_("Cette invitation a déjà été acceptée."))
    if invitation.is_expired:
        raise ValidationError(_("Cette invitation a expiré."))

    if user is None:
        if not password:
            raise ValidationError({"password": _("Mot de passe obligatoire.")})
        existing = UserModel.objects.filter(email__iexact=invitation.email).first()
        if existing:
            raise ValidationError(
                _("Un compte existe déjà pour cet e-mail. Connectez-vous puis acceptez.")
            )
        user = UserModel.objects.create_user(
            email=invitation.email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
    elif user.email.lower() != invitation.email.lower():
        raise ValidationError(_("Cette invitation est destinée à une autre adresse e-mail."))

    membership, _created = Membership.objects.get_or_create(
        cabinet=invitation.cabinet,
        user=user,
        defaults={
            "role": invitation.role,
            "is_active": True,
            "created_by": user,
        },
    )
    if not _created:
        membership.role = invitation.role
        membership.is_active = True
        membership.is_deleted = False
        membership.deleted_at = None
        membership.save()

    invitation.accepted_at = timezone.now()
    invitation.save(update_fields=["accepted_at", "updated_at"])
    return user, membership, invitation


def resolve_cabinet_for_request(request: HttpRequest) -> Cabinet | None:
    """
    Résout le cabinet courant depuis la session.

    Si aucun cabinet en session, prend le premier cabinet de l'utilisateur.
    """
    user = request.user
    if not user.is_authenticated:
        return None

    cabinets = list_user_cabinets(user)  # type: ignore[arg-type]
    if not cabinets:
        return None

    raw_id = request.session.get(SESSION_CABINET_KEY)
    if raw_id:
        for cabinet in cabinets:
            if str(cabinet.pk) == str(raw_id):
                return cabinet

    cabinet = cabinets[0]
    set_session_cabinet(request, cabinet)
    return cabinet


def can_manage_members(*, user: User, cabinet: Cabinet) -> bool:
    """Raccourci manage_members."""
    return user_has_cabinet_perm(user=user, cabinet=cabinet, perm=PERM_MANAGE_MEMBERS)


def can_manage_cabinet(*, user: User, cabinet: Cabinet) -> bool:
    """Raccourci manage_cabinet."""
    return user_has_cabinet_perm(user=user, cabinet=cabinet, perm=PERM_MANAGE_CABINET)
