"""Routes API v1."""

from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.api.views import ClientViewSet, EventViewSet, MatterViewSet

router = DefaultRouter()
router.register("clients", ClientViewSet, basename="api-clients")
router.register("matters", MatterViewSet, basename="api-matters")
router.register("events", EventViewSet, basename="api-events")

urlpatterns = [
    path("v1/", include(router.urls)),
]
