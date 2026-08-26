"""Tribunaux et juridictions de Kinshasa (RDC).

Références : décret n°14/015 du 08/05/2014 (TGI), arrêté portant création
des tribunaux de paix à Kinshasa, organisation judiciaire congolaise.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

# Groupes affichés en optgroup dans les listes déroulantes.
KINSHASA_COURT_GROUPS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        _("Cours suprêmes"),
        [
            ("Cour de cassation", _("Cour de cassation")),
        ],
    ),
    (
        _("Cours d'appel"),
        [
            ("Cour d'appel de Kinshasa/Gombe", _("Cour d'appel de Kinshasa/Gombe")),
            ("Cour d'appel de Kinshasa/Matete", _("Cour d'appel de Kinshasa/Matete")),
        ],
    ),
    (
        _("Tribunaux de grande instance"),
        [
            (
                "Tribunal de grande instance de Kinshasa/Gombe",
                _("Tribunal de grande instance de Kinshasa/Gombe"),
            ),
            (
                "Tribunal de grande instance de Kinshasa/Kalamu",
                _("Tribunal de grande instance de Kinshasa/Kalamu"),
            ),
            (
                "Tribunal de grande instance de Kinshasa/N'djili",
                _("Tribunal de grande instance de Kinshasa/N'djili"),
            ),
            (
                "Tribunal de grande instance de Kinshasa/Kinkole",
                _("Tribunal de grande instance de Kinshasa/Kinkole"),
            ),
        ],
    ),
    (
        _("Tribunaux de paix"),
        [
            (
                "Tribunal de paix de Kinshasa/Ngaliema",
                _("Tribunal de paix de Kinshasa/Ngaliema"),
            ),
            (
                "Tribunal de paix de Kinshasa/Assossa",
                _("Tribunal de paix de Kinshasa/Assossa"),
            ),
            (
                "Tribunal de paix de Kinshasa/Pont Kasa-Vubu",
                _("Tribunal de paix de Kinshasa/Pont Kasa-Vubu"),
            ),
            ("Tribunal de paix de Kinshasa/Gombe", _("Tribunal de paix de Kinshasa/Gombe")),
            ("Tribunal de paix de Kinshasa/Lemba", _("Tribunal de paix de Kinshasa/Lemba")),
            ("Tribunal de paix de Kinshasa/Matete", _("Tribunal de paix de Kinshasa/Matete")),
            ("Tribunal de paix de Kinshasa/N'djili", _("Tribunal de paix de Kinshasa/N'djili")),
            (
                "Tribunal de paix de Kinshasa/Kinkole",
                _("Tribunal de paix de Kinshasa/Kinkole"),
            ),
        ],
    ),
    (
        _("Juridictions spécialisées"),
        [
            ("Tribunal de commerce de la Gombe", _("Tribunal de commerce de la Gombe")),
            ("Tribunal du travail de la Gombe", _("Tribunal du travail de la Gombe")),
            (
                "Tribunal pour enfants de la Gombe",
                _("Tribunal pour enfants de la Gombe"),
            ),
        ],
    ),
]


def kinshasa_court_choices(*, blank: bool = True) -> list[tuple[str, str] | tuple[str, list]]:
    """Choix pour un widget Select (optgroups)."""
    choices: list[tuple[str, str] | tuple[str, list]] = []
    if blank:
        choices.append(("", _("— Sélectionner un tribunal —")))
    choices.extend(KINSHASA_COURT_GROUPS)
    return choices


def kinshasa_court_values() -> frozenset[str]:
    """Ensemble des libellés enregistrables."""
    return frozenset(value for _group, items in KINSHASA_COURT_GROUPS for value, _label in items)


def kinshasa_court_filter_choices() -> list[tuple[str, str]]:
    """Liste plate pour filtres (tous les tribunaux + option vide)."""
    return [("", _("Tous les tribunaux"))] + [
        (value, label) for _group, items in KINSHASA_COURT_GROUPS for value, label in items
    ]


def court_choices_with_value(current: str, *, blank: bool = True) -> list:
    """Inclut une valeur existante hors liste (données antérieures)."""
    known = {value for value in kinshasa_court_values()}
    choices = kinshasa_court_choices(blank=blank)
    if current and current not in known:
        insert_at = 1 if blank else 0
        choices.insert(insert_at, (current, current))
    return choices
