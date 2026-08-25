"""Tests d'isolation multi-tenant (fail-closed)."""

from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured

from apps.tenants.context import cabinet_context
from apps.tenants.models import CabinetPreference
from tests.factories import CabinetFactory, CabinetPreferenceFactory, MembershipFactory, UserFactory


@pytest.mark.django_db
def test_tenant_manager_returns_empty_without_cabinet_context() -> None:
    """Sans cabinet courant, le manager ne renvoie aucune ligne (fail-closed)."""
    cab = CabinetFactory()
    CabinetPreferenceFactory(cabinet=cab, key="theme")
    assert CabinetPreference.objects.count() == 0
    assert CabinetPreference.unscoped.filter(cabinet=cab).count() == 1


@pytest.mark.django_db
def test_tenant_manager_filters_by_current_cabinet() -> None:
    """Le manager ne voit que les objets du cabinet courant."""
    cab_a = CabinetFactory(name="Alpha")
    cab_b = CabinetFactory(name="Beta")
    CabinetPreferenceFactory(cabinet=cab_a, key="a")
    CabinetPreferenceFactory(cabinet=cab_b, key="b")

    with cabinet_context(cab_a):
        keys = list(CabinetPreference.objects.values_list("key", flat=True))
    assert keys == ["a"]

    with cabinet_context(cab_b):
        keys = list(CabinetPreference.objects.values_list("key", flat=True))
    assert keys == ["b"]


@pytest.mark.django_db
def test_cannot_read_other_cabinet_by_pk() -> None:
    """get() sur un PK d'un autre cabinet échoue dans le contexte courant."""
    cab_a = CabinetFactory()
    cab_b = CabinetFactory()
    pref_b = CabinetPreferenceFactory(cabinet=cab_b, key="secret")

    with cabinet_context(cab_a), pytest.raises(CabinetPreference.DoesNotExist):
        CabinetPreference.objects.get(pk=pref_b.pk)


@pytest.mark.django_db
def test_create_injects_current_cabinet() -> None:
    """create() sans cabinet= utilise le ContextVar."""
    cab = CabinetFactory()
    with cabinet_context(cab):
        pref = CabinetPreference.objects.create(key="locale", value={"lang": "fr"})
    assert pref.cabinet_id == cab.pk


@pytest.mark.django_db
def test_create_without_cabinet_raises() -> None:
    """create() sans contexte ni argument lève ImproperlyConfigured."""
    with pytest.raises(ImproperlyConfigured):
        CabinetPreference.objects.create(key="x", value={})


@pytest.mark.django_db
def test_for_cabinet_ignores_context() -> None:
    """for_cabinet() permet un accès explicite contrôlé (services admin)."""
    cab_a = CabinetFactory()
    cab_b = CabinetFactory()
    CabinetPreferenceFactory(cabinet=cab_a, key="a")
    CabinetPreferenceFactory(cabinet=cab_b, key="b")

    with cabinet_context(cab_a):
        assert CabinetPreference.objects.for_cabinet(cab_b).count() == 1


@pytest.mark.django_db
def test_switch_cabinet_denied_without_membership(client) -> None:
    """Un utilisateur ne peut pas activer un cabinet sans adhésion."""
    user = UserFactory(password="Str0ng-Passw0rd!")
    MembershipFactory(user=user, cabinet=CabinetFactory())
    other = CabinetFactory()

    assert client.login(username=user.email, password="Str0ng-Passw0rd!")
    response = client.post("/cabinets/switch/", {"cabinet_id": str(other.pk)})
    assert response.status_code == 302
    # Session ne doit pas contenir l'autre cabinet
    assert client.session.get("cabinet_id") != str(other.pk)
