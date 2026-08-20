"""Fixtures pytest partagées."""

from __future__ import annotations

import pytest

from apps.accounts.models import User
from tests.factories import UserFactory


@pytest.fixture
def user(db: None) -> User:
    """Utilisateur actif de test."""
    return UserFactory(
        email="avocat@example.com",
        password="Str0ng-Passw0rd!",
        first_name="Alice",
        last_name="Martin",
    )
