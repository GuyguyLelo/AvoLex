"""Formulaires dossiers."""

from __future__ import annotations

from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from apps.clients.models import Client
from apps.matters.models import Matter, MatterStatus

User = get_user_model()


class MatterForm(forms.ModelForm):
    """Création / édition d'un dossier."""

    class Meta:
        model = Matter
        fields = (
            "client",
            "title",
            "description",
            "practice_area",
            "jurisdiction",
            "opposing_party",
            "status",
            "responsible_lawyer",
            "opened_at",
            "closed_at",
            "notes",
        )
        widgets = {
            "client": forms.Select(attrs={"class": "form-input"}),
            "title": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 4}),
            "practice_area": forms.TextInput(
                attrs={"class": "form-input", "placeholder": _("Ex. droit du travail")}
            ),
            "jurisdiction": forms.TextInput(attrs={"class": "form-input"}),
            "opposing_party": forms.TextInput(attrs={"class": "form-input"}),
            "status": forms.Select(attrs={"class": "form-input"}),
            "responsible_lawyer": forms.Select(attrs={"class": "form-input"}),
            "opened_at": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "closed_at": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }

    def __init__(
        self,
        *args: Any,
        client_queryset: QuerySet[Client] | None = None,
        lawyer_queryset: QuerySet[Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        if client_queryset is not None:
            self.fields["client"].queryset = client_queryset
        if lawyer_queryset is not None:
            self.fields["responsible_lawyer"].queryset = lawyer_queryset
        self.fields["status"].choices = MatterStatus.choices
