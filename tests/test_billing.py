"""Tests facturation : temps, émission, numérotation, PDF, CSV, isolation."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.core.exceptions import PermissionDenied, ValidationError
from django.urls import reverse

from apps.billing.models import InvoiceStatus, TimeEntry
from apps.billing.services import (
    allocate_invoice_number,
    create_draft_invoice,
    create_expense,
    create_time_entry,
    export_invoices_csv,
    issue_invoice,
    mark_invoice_paid,
    start_timer,
    stop_timer,
)
from apps.tenants.context import cabinet_context
from apps.tenants.roles import Role
from tests.factories import (
    CabinetFactory,
    ClientFactory,
    MatterFactory,
    MembershipFactory,
    UserFactory,
)


@pytest.mark.django_db
def test_time_entry_and_timer() -> None:
    """Saisie manuelle + timer start/stop."""
    user = UserFactory()
    matter = MatterFactory()
    MembershipFactory(user=user, cabinet=matter.cabinet, role=Role.LAWYER)
    with cabinet_context(matter.cabinet):
        entry = create_time_entry(
            cabinet=matter.cabinet,
            user=user,
            matter=matter,
            description="Consultation",
            duration_minutes=90,
            hourly_rate=Decimal("200.00"),
        )
        assert entry.amount == Decimal("300.00")
        timer = start_timer(
            cabinet=matter.cabinet,
            user=user,
            matter=matter,
            description="Appel",
        )
        assert timer.is_running
        stop_timer(entry=timer, user=user)
        timer.refresh_from_db()
        assert not timer.is_running
        assert timer.duration_minutes >= 1


@pytest.mark.django_db
def test_invoice_number_sequence_no_gaps() -> None:
    """Numérotation FAC-YYYY-NNNNN sans trou."""
    cabinet = CabinetFactory()
    with cabinet_context(cabinet):
        n1 = allocate_invoice_number(cabinet=cabinet, year=2026)
        n2 = allocate_invoice_number(cabinet=cabinet, year=2026)
    assert n1 == "FAC-2026-00001"
    assert n2 == "FAC-2026-00002"


@pytest.mark.django_db
def test_issue_invoice_generates_pdf_and_number() -> None:
    """Émission : numéro + statut SENT + PDF."""
    user = UserFactory()
    matter = MatterFactory()
    MembershipFactory(user=user, cabinet=matter.cabinet, role=Role.OWNER)
    with cabinet_context(matter.cabinet):
        create_time_entry(
            cabinet=matter.cabinet,
            user=user,
            matter=matter,
            description="Rédaction",
            duration_minutes=60,
        )
        times = list(
            TimeEntry.objects.filter(cabinet=matter.cabinet, invoice__isnull=True).values_list(
                "pk", flat=True
            )
        )
        invoice = create_draft_invoice(
            cabinet=matter.cabinet,
            user=user,
            client=matter.client,
            matter=matter,
            time_entry_ids=[str(pk) for pk in times],
        )
        assert invoice.status == InvoiceStatus.DRAFT
        assert invoice.lines.count() == 1
        issue_invoice(invoice=invoice, user=user)
        invoice.refresh_from_db()

    assert invoice.status == InvoiceStatus.SENT
    assert invoice.number.startswith("FAC-")
    assert invoice.pdf_file
    assert invoice.total > 0


@pytest.mark.django_db
def test_cannot_issue_empty_invoice() -> None:
    """Facture sans ligne refusée."""
    user = UserFactory()
    client = ClientFactory()
    MembershipFactory(user=user, cabinet=client.cabinet, role=Role.OWNER)
    with cabinet_context(client.cabinet):
        invoice = create_draft_invoice(
            cabinet=client.cabinet,
            user=user,
            client=client,
            matter=None,
        )
        with pytest.raises(ValidationError):
            issue_invoice(invoice=invoice, user=user)


@pytest.mark.django_db
def test_mark_paid_and_csv_export() -> None:
    """Marquage payé + export CSV."""
    user = UserFactory()
    matter = MatterFactory()
    MembershipFactory(user=user, cabinet=matter.cabinet, role=Role.OWNER)
    with cabinet_context(matter.cabinet):
        t = create_time_entry(
            cabinet=matter.cabinet,
            user=user,
            matter=matter,
            description="X",
            duration_minutes=30,
        )
        inv = create_draft_invoice(
            cabinet=matter.cabinet,
            user=user,
            client=matter.client,
            matter=matter,
            time_entry_ids=[str(t.pk)],
        )
        issue_invoice(invoice=inv, user=user)
        inv.refresh_from_db()
        mark_invoice_paid(invoice=inv, user=user)
        inv.refresh_from_db()
        assert inv.status == InvoiceStatus.PAID
        csv_file = export_invoices_csv(cabinet=matter.cabinet, user=user)
        content = csv_file.read().decode("utf-8-sig")
    assert inv.number in content
    assert "paid" in content


@pytest.mark.django_db
def test_billing_isolation() -> None:
    """Temps d'un cabinet invisible dans l'autre."""
    u1 = UserFactory()
    m1 = MatterFactory()
    MembershipFactory(user=u1, cabinet=m1.cabinet, role=Role.LAWYER)
    with cabinet_context(m1.cabinet):
        create_time_entry(
            cabinet=m1.cabinet,
            user=u1,
            matter=m1,
            description="Secret",
            duration_minutes=10,
        )
    cab_b = CabinetFactory()
    with cabinet_context(cab_b):
        assert TimeEntry.objects.count() == 0


@pytest.mark.django_db
def test_expense_and_invoice_http(client) -> None:
    """Flux HTTP création débours + liste factures."""
    user = UserFactory(email="bill@example.com", password="Str0ng-Passw0rd!")
    matter = MatterFactory()
    MembershipFactory(user=user, cabinet=matter.cabinet, role=Role.OWNER)
    assert client.login(username="bill@example.com", password="Str0ng-Passw0rd!")
    session = client.session
    session["cabinet_id"] = str(matter.cabinet_id)
    session.save()

    with cabinet_context(matter.cabinet):
        create_expense(
            cabinet=matter.cabinet,
            user=user,
            matter=matter,
            description="Greffe",
            amount=Decimal("45.00"),
        )

    resp = client.get(reverse("billing:hub"))
    assert resp.status_code == 200
    resp_list = client.get(reverse("billing:expense_list"))
    assert resp_list.status_code == 200
    assert b"Greffe" in resp_list.content


@pytest.mark.django_db
def test_read_only_cannot_create_time() -> None:
    """Lecture seule refusée pour la saisie."""
    user = UserFactory()
    matter = MatterFactory()
    MembershipFactory(user=user, cabinet=matter.cabinet, role=Role.READ_ONLY)
    with cabinet_context(matter.cabinet), pytest.raises(PermissionDenied):
        create_time_entry(
            cabinet=matter.cabinet,
            user=user,
            matter=matter,
            description="Nope",
            duration_minutes=15,
        )


@pytest.mark.django_db
def test_invoice_pdf_download(client) -> None:
    """Le PDF se télécharge après émission."""
    user = UserFactory(email="pdf@example.com", password="Str0ng-Passw0rd!")
    matter = MatterFactory()
    MembershipFactory(user=user, cabinet=matter.cabinet, role=Role.OWNER)
    assert client.login(username="pdf@example.com", password="Str0ng-Passw0rd!")
    with cabinet_context(matter.cabinet):
        entry = create_time_entry(
            cabinet=matter.cabinet,
            user=user,
            matter=matter,
            description="Consultation",
            duration_minutes=60,
        )
        invoice = create_draft_invoice(
            cabinet=matter.cabinet,
            user=user,
            client=matter.client,
            matter=matter,
            time_entry_ids=[str(entry.pk)],
        )
        issue_invoice(invoice=invoice, user=user)
        invoice.refresh_from_db()
    response = client.get(reverse("billing:invoice_pdf", kwargs={"pk": invoice.pk}))
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/pdf")
    body = b"".join(response.streaming_content)
    assert body.startswith(b"%PDF")


@pytest.mark.django_db
def test_fpdf_backend_builds_readable_pdf(settings) -> None:
    """Le backend fpdf2 produit un PDF réel (pas un stub)."""
    settings.BILLING_PDF_BACKEND = "fpdf"
    user = UserFactory()
    matter = MatterFactory()
    MembershipFactory(user=user, cabinet=matter.cabinet, role=Role.OWNER)
    with cabinet_context(matter.cabinet):
        entry = create_time_entry(
            cabinet=matter.cabinet,
            user=user,
            matter=matter,
            description="Plaidoirie",
            duration_minutes=90,
            hourly_rate=Decimal("250.00"),
        )
        invoice = create_draft_invoice(
            cabinet=matter.cabinet,
            user=user,
            client=matter.client,
            matter=matter,
            time_entry_ids=[str(entry.pk)],
        )
        issue_invoice(invoice=invoice, user=user)
        invoice.refresh_from_db()
        data = invoice.pdf_file.read()
    assert data.startswith(b"%PDF")
    assert len(data) > 800
