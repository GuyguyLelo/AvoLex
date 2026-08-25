"""Formulaires tenants."""

from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.tenants.roles import Role


class InviteMemberForm(forms.Form):
    """Invitation d'un collaborateur."""

    email = forms.EmailField(
        label=_("E-mail du collaborateur"),
        widget=forms.EmailInput(attrs={"class": "form-input", "autocomplete": "email"}),
    )
    role = forms.ChoiceField(
        label=_("Rôle"),
        choices=[c for c in Role.choices if c[0] != Role.OWNER],
        widget=forms.Select(attrs={"class": "form-input"}),
    )
