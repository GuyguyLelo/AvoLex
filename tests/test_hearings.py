"""Tests module Audiences."""

from __future__ import annotations

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.calendar_app.models import EventType, HearingStatus
from apps.calendar_app.services import create_event, hearings_queryset, update_hearing_status
from apps.clients.models import ClientType
from apps.clients.services import create_client
from apps.matters.services import create_matter
from apps.tenants.context import cabinet_context
from apps.tenants.roles import Role
from tests.factories import CabinetFactory, MembershipFactory, UserFactory


@pytest.mark.django_db
def test_hearing_create_and_list(client) -> None:  # type: ignore[no-untyped-def]
    """Création audience + liste dédiée."""
    user = UserFactory()
    cabinet = CabinetFactory()
    MembershipFactory(user=user, cabinet=cabinet, role=Role.LAWYER)
    client.force_login(user)
    session = client.session
    session["cabinet_id"] = str(cabinet.pk)
    session.save()

    with cabinet_context(cabinet):
        cl = create_client(
            cabinet=cabinet,
            user=user,
            client_type=ClientType.PERSON,
            last_name="Durand",
        )
        matter = create_matter(
            cabinet=cabinet,
            user=user,
            client=cl,
            title="Litige commercial",
            responsible_lawyer=user,
        )
        hearing = create_event(
            cabinet=cabinet,
            user=user,
            title="Audience de fond",
            starts_at=timezone.now() + timedelta(days=3),
            event_type=EventType.HEARING,
            matter=matter,
            court="Tribunal de grande instance de Kinshasa/Gombe",
            chamber="1re ch. civ.",
        )
        assert hearing.hearing_status == HearingStatus.SCHEDULED

        listed = hearings_queryset(cabinet=cabinet, upcoming_only=True)
        assert listed.filter(pk=hearing.pk).exists()

    resp = client.get(reverse("hearings:list"))
    assert resp.status_code == 200
    assert b"Audience de fond" in resp.content
    assert b"Tribunal de grande instance de Kinshasa/Gombe" in resp.content


@pytest.mark.django_db
def test_hearing_status_update() -> None:
    """Marquer une audience comme tenue."""
    user = UserFactory()
    cabinet = CabinetFactory()
    MembershipFactory(user=user, cabinet=cabinet, role=Role.OWNER)
    with cabinet_context(cabinet):
        hearing = create_event(
            cabinet=cabinet,
            user=user,
            title="Audience référé",
            starts_at=timezone.now() + timedelta(days=1),
            event_type=EventType.HEARING,
            court="Tribunal de paix de Kinshasa/Lemba",
        )
        updated = update_hearing_status(
            event=hearing,
            user=user,
            hearing_status=HearingStatus.HELD,
            hearing_report="Renvoi au 15/09.",
        )
        assert updated.hearing_status == HearingStatus.HELD
        assert updated.is_done is True
        assert "Renvoi" in updated.hearing_report
