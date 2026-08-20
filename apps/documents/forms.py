"""Formulaires GED."""

from __future__ import annotations

from typing import Any

from django import forms
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from apps.documents.services import get_max_upload_bytes
from apps.matters.models import Matter


class DocumentUploadForm(forms.Form):
    """Création d'un document avec fichier initial."""

    matter = forms.ModelChoiceField(
        label=_("Dossier"),
        queryset=Matter.objects.none(),
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    title = forms.CharField(
        label=_("Titre"),
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
        help_text=_("Si vide, le nom du fichier est utilisé."),
    )
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea(attrs={"class": "form-input", "rows": 3}),
    )
    tags = forms.CharField(
        label=_("Tags"),
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": _("contrat, pièce, correspondance"),
            }
        ),
        help_text=_("Séparés par des virgules."),
    )
    file = forms.FileField(
        label=_("Fichier"),
        widget=forms.ClearableFileInput(attrs={"class": "form-input"}),
    )

    def __init__(
        self,
        *args: Any,
        matter_queryset: QuerySet[Matter] | None = None,
        **kwargs: Any,
    ) -> None:
        """Restreint les dossiers au cabinet courant."""
        super().__init__(*args, **kwargs)
        if matter_queryset is not None:
            self.fields["matter"].queryset = matter_queryset

    def clean_file(self) -> object:
        """Vérifie la taille avant le service (contrôle précoce UX)."""
        uploaded = self.cleaned_data["file"]
        max_bytes = get_max_upload_bytes()
        if uploaded.size and uploaded.size > max_bytes:
            raise forms.ValidationError(
                _("Fichier trop volumineux (max %(max)s Mo).") % {"max": max_bytes // (1024 * 1024)}
            )
        return uploaded

    def cleaned_tags(self) -> list[str]:
        """Parse la chaîne de tags."""
        raw = self.cleaned_data.get("tags") or ""
        return [part.strip() for part in raw.split(",") if part.strip()]


class DocumentMetadataForm(forms.Form):
    """Édition des métadonnées."""

    title = forms.CharField(
        label=_("Titre"),
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    description = forms.CharField(
        label=_("Description"),
        required=False,
        widget=forms.Textarea(attrs={"class": "form-input", "rows": 3}),
    )
    tags = forms.CharField(
        label=_("Tags"),
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )

    def cleaned_tags(self) -> list[str]:
        """Parse la chaîne de tags."""
        raw = self.cleaned_data.get("tags") or ""
        return [part.strip() for part in raw.split(",") if part.strip()]


class DocumentVersionForm(forms.Form):
    """Nouvelle version d'un document existant."""

    file = forms.FileField(
        label=_("Nouveau fichier"),
        widget=forms.ClearableFileInput(attrs={"class": "form-input"}),
    )
    change_note = forms.CharField(
        label=_("Note de version"),
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
