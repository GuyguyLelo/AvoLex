"""Tests administrateur plateforme / supervision."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.calendar_app.models import EventType
from apps.calendar_app.services import create_event
from apps.clients.models import ClientType
from apps.clients.services import create_client
from apps.matters.services import create_matter
from apps.tenants.context import cabinet_context
from apps.tenants.roles import PERM_ADD, PERM_VIEW, Role
from apps.tenants.services import is_platform_admin, list_user_cabinets, user_has_cabinet_perm
from tests.factories import CabinetFactory, MembershipFactory, UserFactory


@pytest.mark.django_db
def test_platform_admin_sees_all_cabinets() -> None:
    admin = UserFactory(is_platform_admin=True)
    c1 = CabinetFactory(name="Alpha Law")
    c2 = CabinetFactory(name="Beta Law")
    MembershipFactory(user=UserFactory(), cabinet=c1, role=Role.OWNER)
    MembershipFactory(user=UserFactory(), cabinet=c2, role=Role.OWNER)

    cabinets = list_user_cabinets(admin)
    names = {c.name for c in cabinets}
    assert "Alpha Law" in names
    assert "Beta Law" in names
    assert is_platform_admin(admin)


@pytest.mark.django_db
def test_platform_admin_read_only_perms() -> None:
    admin = UserFactory(is_platform_admin=True)
    cabinet = CabinetFactory()
    assert user_has_cabinet_perm(user=admin, cabinet=cabinet, perm=PERM_VIEW) is True
    assert user_has_cabinet_perm(user=admin, cabinet=cabinet, perm=PERM_ADD) is False


@pytest.mark.django_db
def test_supervision_page(client) -> None:  # type: ignore[no-untyped-def]
    admin = UserFactory(is_platform_admin=True)
    cabinet = CabinetFactory(name="ILEO Law Firm")
    owner = UserFactory()
    MembershipFactory(user=owner, cabinet=cabinet, role=Role.OWNER)

    with cabinet_context(cabinet):
        cl = create_client(
            cabinet=cabinet,
            user=owner,
            client_type=ClientType.PERSON,
            last_name="Kabasele",
        )
        matter = create_matter(
            cabinet=cabinet,
            user=owner,
            client=cl,
            title="Affaire commerciale",
            responsible_lawyer=owner,
        )
        create_event(
            cabinet=cabinet,
            user=owner,
            title="Audience TGI Gombe",
            starts_at=timezone.now() + timedelta(days=2),
            event_type=EventType.HEARING,
            matter=matter,
            court="Tribunal de grande instance de Kinshasa/Gombe",
        )

    client.force_login(admin)
    resp = client.get(reverse("core:supervision"))
    assert resp.status_code == 200
    assert b"ILEO Law Firm" in resp.content
    assert b"Supervision" in resp.content
    assert b"Audience TGI Gombe" in resp.content


@pytest.mark.django_db
def test_regular_user_cannot_access_supervision(client) -> None:  # type: ignore[no-untyped-def]
    user = UserFactory()
    cabinet = CabinetFactory()
    MembershipFactory(user=user, cabinet=cabinet, role=Role.LAWYER)
    client.force_login(user)
    session = client.session
    session["cabinet_id"] = str(cabinet.pk)
    session.save()
    resp = client.get(reverse("core:supervision"))
    assert resp.status_code == 403
