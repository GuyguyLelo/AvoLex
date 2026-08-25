"""URLs agenda."""

from __future__ import annotations

from django.urls import path

from apps.calendar_app import views

app_name = "calendar"

urlpatterns = [
    path("", views.CalendarListView.as_view(), name="list"),
    path("nouveau/", views.EventCreateView.as_view(), name="event_create"),
    path("<uuid:pk>/", views.EventDetailView.as_view(), name="event_detail"),
    path("<uuid:pk>/modifier/", views.EventUpdateView.as_view(), name="event_update"),
    path("<uuid:pk>/termine/", views.EventDoneView.as_view(), name="event_done"),
    path("<uuid:pk>/supprimer/", views.EventDeleteView.as_view(), name="event_delete"),
]
