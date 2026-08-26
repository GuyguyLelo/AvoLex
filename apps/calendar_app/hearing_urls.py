"""URLs module Audiences."""

from __future__ import annotations

from django.urls import path

from apps.calendar_app import views

app_name = "hearings"

urlpatterns = [
    path("", views.HearingListView.as_view(), name="list"),
    path("nouvelle/", views.HearingCreateView.as_view(), name="create"),
    path("<uuid:pk>/modifier/", views.HearingUpdateView.as_view(), name="update"),
    path("<uuid:pk>/statut/", views.HearingStatusView.as_view(), name="status"),
]
