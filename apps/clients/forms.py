"""Formulaires clients."""

from __future__ import annotations

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.clients.models import Client, ClientType


class ClientForm(forms.ModelForm):
    """Création / édition d'un client."""

    class Meta:
        model = Client
        fields = (
            "client_type",
            "first_name",
            "last_name",
            "birth_date",
            "company_name",
            "siret",
            "legal_form",
            "email",
            "phone",
            "address_line1",
            "address_line2",
            "postal_code",
            "city",
            "country",
            "notes",
        )
        widgets = {
            "client_type": forms.Select(attrs={"class": "form-input"}),
            "first_name": forms.TextInput(attrs={"class": "form-input"}),
            "last_name": forms.TextInput(attrs={"class": "form-input"}),
            "birth_date": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "company_name": forms.TextInput(attrs={"class": "form-input"}),
            "siret": forms.TextInput(attrs={"class": "form-input"}),
            "legal_form": forms.TextInput(attrs={"class": "form-input"}),
            "email": forms.EmailInput(attrs={"class": "form-input"}),
            "phone": forms.TextInput(attrs={"class": "form-input"}),
            "address_line1": forms.TextInput(attrs={"class": "form-input"}),
            "address_line2": forms.TextInput(attrs={"class": "form-input"}),
            "postal_code": forms.TextInput(attrs={"class": "form-input"}),
            "city": forms.TextInput(attrs={"class": "form-input"}),
            "country": forms.TextInput(attrs={"class": "form-input", "maxlength": "2"}),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "rows": 3,
                    "placeholder": _("Contexte, conflit potentiel, remarques…"),
                }
            ),
        }

    def clean(self) -> dict:
        cleaned = super().clean()
        client_type = cleaned.get("client_type") or ClientType.PERSON
        if client_type == ClientType.COMPANY:
            if not (cleaned.get("company_name") or "").strip():
                self.add_error("company_name", _("La raison sociale est obligatoire."))
            cleaned["first_name"] = ""
            cleaned["last_name"] = ""
            cleaned["birth_date"] = None
        else:
            if not (cleaned.get("last_name") or "").strip():
                self.add_error("last_name", _("Le nom est obligatoire."))
            cleaned["company_name"] = ""
            cleaned["siret"] = ""
            cleaned["legal_form"] = ""
        return cleaned
