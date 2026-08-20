"""Formulaires agenda."""

from __future__ import annotations

from typing import Any

from django import forms
from django.db.models import QuerySet

from apps.calendar_app.models import Event, EventType
from apps.matters.models import Matter


class EventForm(forms.ModelForm):
    """Création / édition d'événement ou tâche."""

    class Meta:
        model = Event
        fields = (
            "event_type",
            "title",
            "matter",
            "description",
            "starts_at",
            "ends_at",
            "all_day",
            "location",
            "remind_at",
        )
        widgets = {
            "event_type": forms.Select(attrs={"class": "form-input"}),
            "title": forms.TextInput(attrs={"class": "form-input"}),
            "matter": forms.Select(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "starts_at": forms.DateTimeInput(
                attrs={"class": "form-input", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "ends_at": forms.DateTimeInput(
                attrs={"class": "form-input", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "all_day": forms.CheckboxInput(),
            "location": forms.TextInput(attrs={"class": "form-input"}),
            "remind_at": forms.DateTimeInput(
                attrs={"class": "form-input", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
        }

    def __init__(
        self,
        *args: Any,
        matter_queryset: QuerySet[Matter] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.fields["starts_at"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]
        self.fields["ends_at"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]
        self.fields["remind_at"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]
        self.fields["event_type"].choices = EventType.choices
        if matter_queryset is not None:
            self.fields["matter"].queryset = matter_queryset
            self.fields["matter"].required = False
