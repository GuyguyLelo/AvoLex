"""Tests API REST (permissions, soft-delete)."""

from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.calendar_app.models import Event, EventType
from apps.calendar_app.services import create_event
from apps.tenants.context import cabinet_context
from apps.tenants.roles import Role
from tests.factories import CabinetFactory, MembershipFactory, UserFactory


@pytest.mark.django_db
def test_api_read_only_cannot_create_client(client) -> None:  # type: ignore[no-untyped-def]
    """Un rôle lecture seule ne peut pas POST sur l'API clients."""
    user = UserFactory()
    cabinet = CabinetFactory()
    MembershipFactory(user=user, cabinet=cabinet, role=Role.READ_ONLY)
    client.force_login(user)
    session = client.session
    session["cabinet_id"] = str(cabinet.pk)
    session.save()

    response = client.post(
        "/api/v1/clients/",
        {"client_type": "person", "first_name": "Test", "last_name": "User"},
        content_type="application/json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_api_event_soft_delete(client) -> None:  # type: ignore[no-untyped-def]
    """DELETE /api/v1/events/ soft-delete l'événement (pas de hard-delete)."""
    user = UserFactory()
    cabinet = CabinetFactory()
    MembershipFactory(user=user, cabinet=cabinet, role=Role.OWNER)
    client.force_login(user)
    session = client.session
    session["cabinet_id"] = str(cabinet.pk)
    session.save()

    with cabinet_context(cabinet):
        event = create_event(
            cabinet=cabinet,
            user=user,
            title="À supprimer",
            starts_at=timezone.now(),
            event_type=EventType.APPOINTMENT,
        )
        event_pk = event.pk

    response = client.delete(f"/api/v1/events/{event_pk}/")
    assert response.status_code == 204

    with cabinet_context(cabinet):
        assert not Event.objects.filter(pk=event_pk).exists()
        assert Event.all_objects.filter(pk=event_pk, is_deleted=True).exists()
