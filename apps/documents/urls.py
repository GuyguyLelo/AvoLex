"""URLs GED."""

from __future__ import annotations

from django.urls import path

from apps.documents import views

app_name = "documents"

urlpatterns = [
    path("", views.DocumentListView.as_view(), name="list"),
    path("upload/", views.DocumentUploadView.as_view(), name="upload"),
    path("<uuid:pk>/", views.DocumentDetailView.as_view(), name="detail"),
    path("<uuid:pk>/edit/", views.DocumentUpdateMetadataView.as_view(), name="edit"),
    path("<uuid:pk>/versions/", views.DocumentAddVersionView.as_view(), name="add_version"),
    path("<uuid:pk>/delete/", views.DocumentDeleteView.as_view(), name="delete"),
    path(
        "versions/<uuid:version_id>/download/",
        views.DocumentDownloadView.as_view(),
        name="download",
    ),
    path(
        "versions/<uuid:version_id>/preview/",
        views.DocumentPreviewView.as_view(),
        name="preview",
    ),
]
