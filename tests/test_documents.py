"""Tests GED : upload, versioning, isolation, téléchargement protégé."""

from __future__ import annotations

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.documents.models import Document, DocumentVersion
from apps.documents.services import (
    add_document_version,
    create_document_with_file,
    get_version_for_download,
)
from apps.tenants.context import cabinet_context
from apps.tenants.roles import Role
from tests.factories import CabinetFactory, MatterFactory, MembershipFactory, UserFactory


def _pdf_upload(name: str = "piece.pdf", content: bytes = b"%PDF-1.4 test") -> SimpleUploadedFile:
    """Fichier PDF minimal pour les tests."""
    return SimpleUploadedFile(name, content, content_type="application/pdf")


@pytest.mark.django_db
def test_create_document_with_version() -> None:
    """Upload crée document + version 1 courante."""
    user = UserFactory()
    matter = MatterFactory()
    MembershipFactory(user=user, cabinet=matter.cabinet, role=Role.LAWYER)
    uploaded = _pdf_upload()

    with cabinet_context(matter.cabinet):
        document = create_document_with_file(
            cabinet=matter.cabinet,
            matter=matter,
            user=user,
            title="Pièce adverse",
            uploaded_file=uploaded,
            filename=uploaded.name,
            content_type=uploaded.content_type,
            tags=["Pièce", "pièce", " adverse "],
        )

    assert document.title == "Pièce adverse"
    assert document.tags == ["pièce", "adverse"]
    assert document.current_version is not None
    assert document.current_version.version_number == 1
    assert document.current_version.checksum
    assert document.current_version.size > 0


@pytest.mark.django_db
def test_add_version_increments() -> None:
    """Une nouvelle version incrémente le numéro et devient courante."""
    user = UserFactory()
    matter = MatterFactory()
    MembershipFactory(user=user, cabinet=matter.cabinet, role=Role.LAWYER)
    with cabinet_context(matter.cabinet):
        document = create_document_with_file(
            cabinet=matter.cabinet,
            matter=matter,
            user=user,
            title="Contrat",
            uploaded_file=_pdf_upload("v1.pdf", b"%PDF-1.4 v1"),
            filename="v1.pdf",
            content_type="application/pdf",
        )
        v2 = add_document_version(
            document=document,
            user=user,
            uploaded_file=_pdf_upload("v2.pdf", b"%PDF-1.4 v2-content"),
            filename="v2.pdf",
            content_type="application/pdf",
            change_note="Correction",
        )
        document.refresh_from_db()

    assert v2.version_number == 2
    assert document.current_version_id == v2.pk


@pytest.mark.django_db
def test_reject_disallowed_mime() -> None:
    """Les exécutables sont refusés."""
    user = UserFactory()
    matter = MatterFactory()
    MembershipFactory(user=user, cabinet=matter.cabinet, role=Role.OWNER)
    bad = SimpleUploadedFile("malware.exe", b"MZ", content_type="application/x-msdownload")
    with cabinet_context(matter.cabinet), pytest.raises(ValidationError):
        create_document_with_file(
            cabinet=matter.cabinet,
            matter=matter,
            user=user,
            title="Bad",
            uploaded_file=bad,
            filename=bad.name,
            content_type=bad.content_type,
        )


@pytest.mark.django_db
def test_tenant_isolation_on_documents() -> None:
    """Les documents d'un autre cabinet sont invisibles."""
    user_a = UserFactory()
    cab_a = CabinetFactory()
    cab_b = CabinetFactory()
    MembershipFactory(user=user_a, cabinet=cab_a, role=Role.OWNER)
    matter_a = MatterFactory(cabinet=cab_a)
    matter_b = MatterFactory(cabinet=cab_b)

    with cabinet_context(cab_a):
        create_document_with_file(
            cabinet=cab_a,
            matter=matter_a,
            user=user_a,
            title="Secret A",
            uploaded_file=_pdf_upload(),
            filename="a.pdf",
            content_type="application/pdf",
        )
    user_b = UserFactory()
    MembershipFactory(user=user_b, cabinet=cab_b, role=Role.OWNER)
    with cabinet_context(cab_b):
        create_document_with_file(
            cabinet=cab_b,
            matter=matter_b,
            user=user_b,
            title="Secret B",
            uploaded_file=_pdf_upload("b.pdf"),
            filename="b.pdf",
            content_type="application/pdf",
        )
        titles = list(Document.objects.values_list("title", flat=True))

    assert titles == ["Secret B"]


@pytest.mark.django_db
def test_download_denied_cross_tenant() -> None:
    """Impossible de télécharger une version hors cabinet."""
    owner_a = UserFactory()
    cab_a = CabinetFactory()
    cab_b = CabinetFactory()
    MembershipFactory(user=owner_a, cabinet=cab_a, role=Role.OWNER)
    matter = MatterFactory(cabinet=cab_a)
    with cabinet_context(cab_a):
        doc = create_document_with_file(
            cabinet=cab_a,
            matter=matter,
            user=owner_a,
            title="Doc",
            uploaded_file=_pdf_upload(),
            filename="a.pdf",
            content_type="application/pdf",
        )
        version_id = str(doc.current_version_id)

    outsider = UserFactory()
    MembershipFactory(user=outsider, cabinet=cab_b, role=Role.OWNER)
    with pytest.raises(DocumentVersion.DoesNotExist):
        get_version_for_download(version_id=version_id, user=outsider, cabinet=cab_b)


@pytest.mark.django_db
def test_read_only_cannot_upload() -> None:
    """Lecture seule ne peut pas téléverser."""
    user = UserFactory()
    matter = MatterFactory()
    MembershipFactory(user=user, cabinet=matter.cabinet, role=Role.READ_ONLY)
    with cabinet_context(matter.cabinet), pytest.raises(PermissionDenied):
        create_document_with_file(
            cabinet=matter.cabinet,
            matter=matter,
            user=user,
            title="Nope",
            uploaded_file=_pdf_upload(),
            filename="a.pdf",
            content_type="application/pdf",
        )


@pytest.mark.django_db
def test_document_list_and_download_http(client) -> None:
    """Flux HTTP : liste + téléchargement authentifié."""
    user = UserFactory(email="ged@example.com", password="Str0ng-Passw0rd!")
    matter = MatterFactory()
    MembershipFactory(user=user, cabinet=matter.cabinet, role=Role.LAWYER)
    with cabinet_context(matter.cabinet):
        document = create_document_with_file(
            cabinet=matter.cabinet,
            matter=matter,
            user=user,
            title="Courrier",
            uploaded_file=_pdf_upload(content=b"%PDF-1.4 courrier"),
            filename="courrier.pdf",
            content_type="application/pdf",
        )
        version_id = document.current_version_id

    assert client.login(username="ged@example.com", password="Str0ng-Passw0rd!")
    session = client.session
    session["cabinet_id"] = str(matter.cabinet_id)
    session.save()

    list_resp = client.get(reverse("documents:list"))
    assert list_resp.status_code == 200
    assert b"Courrier" in list_resp.content

    dl = client.get(reverse("documents:download", kwargs={"version_id": version_id}))
    assert dl.status_code == 200
    assert dl["Content-Disposition"].startswith("attachment")
    assert b"%PDF" in b"".join(dl.streaming_content)


@pytest.mark.django_db
def test_private_storage_has_no_public_url() -> None:
    """Le storage refuse de générer une URL publique."""
    from apps.documents.storage import private_document_storage

    with pytest.raises(ValueError):
        private_document_storage.url("anything.pdf")
