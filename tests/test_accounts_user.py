"""Tests du modèle User (identifiant e-mail)."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_create_user_with_email() -> None:
    """Un utilisateur est créé avec e-mail normalisé."""
    user = User.objects.create_user(email="Jean.Dupont@Example.COM", password="secret-pass-99")
    assert user.email == "Jean.Dupont@example.com"
    assert user.check_password("secret-pass-99")
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.timezone == "Europe/Paris"


@pytest.mark.django_db
def test_create_superuser() -> None:
    """Un superutilisateur a les flags staff/superuser."""
    admin = User.objects.create_superuser(email="admin@avolex.local", password="admin-pass-99")
    assert admin.is_staff is True
    assert admin.is_superuser is True


@pytest.mark.django_db
def test_user_str_and_names() -> None:
    """Repr et noms complets sont cohérents."""
    user = User.objects.create_user(
        email="seul@example.com",
        password="x",
        first_name="Claire",
        last_name="Bernard",
    )
    assert str(user) == "seul@example.com"
    assert user.get_full_name() == "Claire Bernard"
    assert user.get_short_name() == "Claire"


@pytest.mark.django_db
def test_create_user_requires_email() -> None:
    """L'e-mail est obligatoire."""
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password="x")
