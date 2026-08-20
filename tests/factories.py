"""Factories factory_boy pour les tests."""

from __future__ import annotations

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from factory.django import DjangoModelFactory

from apps.clients.models import Client, ClientType
from apps.matters.models import Matter, MatterStatus
from apps.tenants.models import Cabinet, CabinetPreference, Invitation, Membership
from apps.tenants.roles import Role

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Utilisateur de test."""

    class Meta:
        model = User
        django_get_or_create = ("email",)

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name", locale="fr_FR")
    last_name = factory.Faker("last_name", locale="fr_FR")
    is_active = True

    @factory.post_generation
    def password(self, create: bool, extracted: str | None, **kwargs: object) -> None:
        """Définit un mot de passe connu."""
        pwd = extracted or "Str0ng-Passw0rd!"
        self.set_password(pwd)
        if create:
            self.save(update_fields=["password"])


class CabinetFactory(DjangoModelFactory):
    """Cabinet de test."""

    class Meta:
        model = Cabinet

    name = factory.Sequence(lambda n: f"Cabinet {n}")
    slug = factory.Sequence(lambda n: f"cabinet-{n}")


class MembershipFactory(DjangoModelFactory):
    """Adhésion user ↔ cabinet."""

    class Meta:
        model = Membership

    user = factory.SubFactory(UserFactory)
    cabinet = factory.SubFactory(CabinetFactory)
    role = Role.LAWYER
    is_active = True


class InvitationFactory(DjangoModelFactory):
    """Invitation de test."""

    class Meta:
        model = Invitation

    cabinet = factory.SubFactory(CabinetFactory)
    email = factory.Sequence(lambda n: f"invite{n}@example.com")
    role = Role.ASSOCIATE
    invited_by = factory.SubFactory(UserFactory)


class CabinetPreferenceFactory(DjangoModelFactory):
    """Préférence tenant-scoped (tests d'isolation)."""

    class Meta:
        model = CabinetPreference

    cabinet = factory.SubFactory(CabinetFactory)
    key = factory.Sequence(lambda n: f"pref-{n}")
    value = factory.LazyFunction(dict)


class ClientFactory(DjangoModelFactory):
    """Client de test."""

    class Meta:
        model = Client

    cabinet = factory.SubFactory(CabinetFactory)
    client_type = ClientType.PERSON
    first_name = factory.Faker("first_name", locale="fr_FR")
    last_name = factory.Faker("last_name", locale="fr_FR")


class MatterFactory(DjangoModelFactory):
    """Dossier de test."""

    class Meta:
        model = Matter

    cabinet = factory.SubFactory(CabinetFactory)
    client = factory.SubFactory(ClientFactory, cabinet=factory.SelfAttribute("..cabinet"))
    responsible_lawyer = factory.SubFactory(UserFactory)
    reference = factory.Sequence(lambda n: f"DOS-2026-{n:04d}")
    title = factory.Sequence(lambda n: f"Affaire {n}")
    status = MatterStatus.OPEN
    opened_at = factory.LazyFunction(lambda: timezone.localdate())
