"""URLs tenants."""

from __future__ import annotations

from django.urls import path

from apps.tenants import views

app_name = "tenants"

urlpatterns = [
    path("switch/", views.SwitchCabinetView.as_view(), name="switch"),
    path("invitations/", views.InvitationListView.as_view(), name="invitation_list"),
    path("invitations/new/", views.InviteMemberView.as_view(), name="invite"),
]
