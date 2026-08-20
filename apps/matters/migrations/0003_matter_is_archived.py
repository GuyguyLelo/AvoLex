"""Champ is_archived sur Matter."""

from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("matters", "0002_complete_crud"),
    ]

    operations = [
        migrations.AddField(
            model_name="matter",
            name="is_archived",
            field=models.BooleanField(db_index=True, default=False, verbose_name="archivé"),
        ),
    ]
