"""Tests clients / dossiers / agenda / dashboard."""

from __future__ import annotations

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.calendar_app.models import EventType
from apps.calendar_app.services import create_event
from apps.clients.models import ClientType
from apps.clients.services import create_client
from apps.core.dashboard import build_dashboard_stats
from apps.matters.models import MatterStatus
from apps.matters.services import archive_matter, create_matter, soft_delete_matter, update_matter
from apps.tenants.context import cabinet_context
from apps.tenants.roles import Role
from tests.factories import CabinetFactory, MembershipFactory, UserFactory


@pytest.mark.django_db
def test_client_matter_flow_and_history() -> None:
    """Création client + dossier + entrée d'historique."""
    user = UserFactory()
    cabinet = CabinetFactory()
    MembershipFactory(user=user, cabinet=cabinet, role=Role.OWNER)
    with cabinet_context(cabinet):
        client = create_client(
            cabinet=cabinet,
            user=user,
            client_type=ClientType.PERSON,
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
        )
        matter = create_matter(
            cabinet=cabinet,
            user=user,
            client=client,
            title="Affaire test",
            responsible_lawyer=user,
            practice_area="Civil",
        )
        assert matter.reference.startswith("DOS-")
        assert matter.actions.filter(action="created").exists()
        stats = build_dashboard_stats(cabinet=cabinet)
        assert stats.clients_count == 1
        assert stats.matters_active == 1


@pytest.mark.django_db
def test_clients_list_http(client) -> None:  # type: ignore[no-untyped-def]
    """Liste clients accessible au membre."""
    user = UserFactory()
    cabinet = CabinetFactory()
    MembershipFactory(user=user, cabinet=cabinet, role=Role.LAWYER)
    client.force_login(user)
    session = client.session
    session["cabinet_id"] = str(cabinet.pk)
    session.save()
    with cabinet_context(cabinet):
        create_client(
            cabinet=cabinet,
            user=user,
            client_type=ClientType.PERSON,
            first_name="Bob",
            last_name="Martin",
        )
    resp = client.get(reverse("clients:list"))
    assert resp.status_code == 200
    assert b"Martin" in resp.content


@pytest.mark.django_db
def test_calendar_event_and_api(client) -> None:  # type: ignore[no-untyped-def]
    """Événement agenda + endpoint API clients."""
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
            title="RDV client",
            starts_at=timezone.now(),
            event_type=EventType.APPOINTMENT,
        )
    resp = client.get(reverse("calendar:list"))
    assert resp.status_code == 200
    assert b"RDV client" in resp.content
    detail = client.get(reverse("calendar:event_detail", kwargs={"pk": event.pk}))
    assert detail.status_code == 200
    assert b"RDV client" in detail.content
    api = client.get("/api/v1/clients/")
    assert api.status_code == 200


@pytest.mark.django_db
def test_closed_matter_cannot_be_deleted_but_can_be_archived() -> None:
    """Un dossier clos est archivable, pas supprimable."""
    user = UserFactory()
    cabinet = CabinetFactory()
    MembershipFactory(user=user, cabinet=cabinet, role=Role.OWNER)
    with cabinet_context(cabinet):
        client = create_client(
            cabinet=cabinet,
            user=user,
            client_type=ClientType.PERSON,
            first_name="Claire",
            last_name="Arch",
        )
        matter = create_matter(
            cabinet=cabinet,
            user=user,
            client=client,
            title="Affaire close",
            responsible_lawyer=user,
        )
        update_matter(
            matter=matter,
            user=user,
            status=MatterStatus.CLOSED,
        )
        matter.refresh_from_db()
        with pytest.raises(Exception) as exc:
            soft_delete_matter(matter=matter, user=user)
        assert "clos" in str(exc.value).lower() or "archiv" in str(exc.value).lower()
        archived = archive_matter(matter=matter, user=user)
        assert archived.is_archived is True
        assert archived.actions.filter(action="archived").exists()
