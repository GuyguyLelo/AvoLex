"""Tests liste des tribunaux de Kinshasa."""

from apps.core.kinshasa_courts import kinshasa_court_values


def test_kinshasa_courts_include_main_jurisdictions() -> None:
    """Les principales juridictions kinshasaises sont présentes."""
    values = kinshasa_court_values()
    assert "Cour de cassation" in values
    assert "Cour d'appel de Kinshasa/Gombe" in values
    assert "Tribunal de grande instance de Kinshasa/Gombe" in values
    assert "Tribunal de paix de Kinshasa/Gombe" in values
    assert "Tribunal de commerce de la Gombe" in values
    assert len(values) >= 18


def test_hearing_form_renders_court_options() -> None:
    """Le formulaire audience affiche les tribunaux dans la liste déroulante."""
    from apps.calendar_app.forms import HearingForm

    html = str(HearingForm()["court"])
    assert html.count("<option") >= 18
    assert "Tribunal de paix de Kinshasa/Gombe" in html
    assert "<optgroup" in html
