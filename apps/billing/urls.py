"""URLs facturation."""

from __future__ import annotations

from django.urls import path

from apps.billing import views

app_name = "billing"

urlpatterns = [
    path("", views.BillingHubView.as_view(), name="hub"),
    path("temps/", views.TimeEntryListView.as_view(), name="time_list"),
    path("temps/nouveau/", views.TimeEntryCreateView.as_view(), name="time_create"),
    path("temps/timer/start/", views.TimerStartView.as_view(), name="timer_start"),
    path("temps/timer/<uuid:pk>/stop/", views.TimerStopView.as_view(), name="timer_stop"),
    path("temps/<uuid:pk>/delete/", views.TimeEntryDeleteView.as_view(), name="time_delete"),
    path("debours/", views.ExpenseListView.as_view(), name="expense_list"),
    path("debours/nouveau/", views.ExpenseCreateView.as_view(), name="expense_create"),
    path("debours/<uuid:pk>/delete/", views.ExpenseDeleteView.as_view(), name="expense_delete"),
    path("factures/", views.InvoiceListView.as_view(), name="invoice_list"),
    path("factures/nouvelle/", views.InvoiceCreateView.as_view(), name="invoice_create"),
    path("factures/export.csv", views.InvoiceExportCsvView.as_view(), name="invoice_export"),
    path("factures/<uuid:pk>/", views.InvoiceDetailView.as_view(), name="invoice_detail"),
    path("factures/<uuid:pk>/emit/", views.InvoiceIssueView.as_view(), name="invoice_issue"),
    path("factures/<uuid:pk>/paid/", views.InvoiceMarkPaidView.as_view(), name="invoice_paid"),
    path(
        "factures/<uuid:pk>/overdue/",
        views.InvoiceMarkOverdueView.as_view(),
        name="invoice_overdue",
    ),
    path("factures/<uuid:pk>/cancel/", views.InvoiceCancelView.as_view(), name="invoice_cancel"),
    path("factures/<uuid:pk>/pdf/", views.InvoicePdfDownloadView.as_view(), name="invoice_pdf"),
]
