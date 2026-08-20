"""URLs accounts."""

from __future__ import annotations

from django.urls import path

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.AvoLexLoginView.as_view(), name="login"),
    path("logout/", views.AvoLexLogoutView.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("password-reset/", views.AvoLexPasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/done/",
        views.AvoLexPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        views.AvoLexPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        views.AvoLexPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(
        "invitations/<str:token>/",
        views.AcceptInvitationView.as_view(),
        name="accept_invitation",
    ),
]
