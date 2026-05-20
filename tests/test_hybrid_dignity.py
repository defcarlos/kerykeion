# -*- coding: utf-8 -*-
import pytest
from kerykeion.astrological_subject_factory import AstrologicalSubjectFactory
from kerykeion.report import ReportGenerator

def test_tropical_vedic_hybrid_dignity():
    """
    Test the "Tropical Vedic" use case:
    - Subject calculated with Tropical Zodiac.
    - Report requested with Vedic Paradigm.
    - Verify that Vedic dignity labels (e.g., 'Enemy', 'Friend') are used
      instead of Western ones (e.g., 'Detriment', 'Fall').
    """
    
    # John Lennon, Tropical
    subject = AstrologicalSubjectFactory.from_birth_data(
        name="John Lennon",
        year=1940,
        month=10,
        day=9,
        hour=18,
        minute=30,
        city="Liverpool",
        nation="GB",
        online=False,
        lng=-2.9779,
        lat=53.4106,
        tz_str="Europe/London",
        zodiac_type="Tropical"
    )
    
    # In Tropical, Sun is in Libra (17° approx)
    sun = subject.sun
    assert sun.sign == "Lib"
    
    # Western: Fall
    # Vedic: Debilitated (Sun is debilitated in Libra)
    assert sun.western_dignity == "Fall"
    assert sun.vedic_dignity == "Debilitated"
    
    # Generate reports and verify labels
    western_report = ReportGenerator(subject, paradigm="Western").generate_report()
    vedic_report = ReportGenerator(subject, paradigm="Vedic").generate_report()
    
    # Verify headers/labels in the report string
    assert "Dignity (Western)" in western_report
    assert "Fall" in western_report
    
    assert "Dignity (Vedic)" in vedic_report
    assert "Debilitated" in vedic_report
    assert "Fall" not in vedic_report # Should not show Western term in Vedic paradigm

def test_sidereal_western_hybrid_dignity():
    """
    Test the inverse hybrid use case:
    - Subject calculated with Sidereal Zodiac.
    - Report requested with Western Paradigm.
    """
    subject = AstrologicalSubjectFactory.from_birth_data(
        name="John Lennon",
        year=1940,
        month=10,
        day=9,
        hour=18,
        minute=30,
        city="Liverpool",
        nation="GB",
        online=False,
        lng=-2.9779,
        lat=53.4106,
        tz_str="Europe/London",
        zodiac_type="Sidereal",
        sidereal_mode="LAHIRI"
    )
    
    # In Sidereal Lahiri, Sun is in Virgo (23° approx)
    sun = subject.sun
    assert sun.sign == "Vir"
    
    # Western: Peregrine (Sun has no dignity in Virgo)
    # Vedic: Neutral (Sun in Virgo, ruled by Mercury. Sun/Mercury are neutral/friends)
    assert sun.western_dignity == "Peregrine"
    assert sun.vedic_dignity == "Neutral"
    
    western_report = ReportGenerator(subject, paradigm="Western").generate_report()
    assert "Dignity (Western)" in western_report
    assert "Peregrine" in western_report

if __name__ == "__main__":
    pytest.main([__file__])
