"""URLs clients."""

from __future__ import annotations

from django.urls import path

from apps.clients import views

app_name = "clients"

urlpatterns = [
    path("", views.ClientListView.as_view(), name="list"),
    path("nouveau/", views.ClientCreateView.as_view(), name="create"),
    path("<uuid:pk>/", views.ClientDetailView.as_view(), name="detail"),
    path("<uuid:pk>/modifier/", views.ClientUpdateView.as_view(), name="update"),
    path("<uuid:pk>/supprimer/", views.ClientDeleteView.as_view(), name="delete"),
]
