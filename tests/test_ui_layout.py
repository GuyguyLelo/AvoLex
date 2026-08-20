"""Tests smoke UI / landing / assets."""

from __future__ import annotations

import pytest
from django.urls import reverse

from tests.factories import MembershipFactory, UserFactory


@pytest.mark.django_db
def test_landing_contains_brand_and_sections(client) -> None:
    """La landing expose la marque et les modules."""
    response = client.get(reverse("core:landing"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "AvoLex" in content or "Avo<span>Lex</span>" in content
    assert 'id="fonctionnalites"' in content
    assert reverse("accounts:register") in content


@pytest.mark.django_db
def test_landing_loads_design_css(client) -> None:
    """Les feuilles de style du design system sont référencées."""
    response = client.get(reverse("core:landing"))
    content = response.content.decode()
    assert "css/base.css" in content
    assert "css/components.css" in content
    assert "css/landing.css" in content


@pytest.mark.django_db
def test_app_shell_has_sidebar_and_topbar(client) -> None:
    """Le shell applicatif contient sidebar et topbar."""
    user = UserFactory(email="ui@example.com", password="Str0ng-Passw0rd!")
    MembershipFactory(user=user)
    assert client.login(username="ui@example.com", password="Str0ng-Passw0rd!")

    response = client.get(reverse("core:home"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "app-sidebar" in content
    assert "app-topbar" in content
    assert "data-sidebar-toggle" in content
    assert "js/main.js" in content
