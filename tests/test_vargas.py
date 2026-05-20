# -*- coding: utf-8 -*-
"""
Tests for Varga (Divisional Charts) calculations.
"""

import pytest
from kerykeion import AstrologicalSubjectFactory
from kerykeion.varga_factory import VargaFactory

def test_lennon_vargas():
    # John Lennon, 1940-10-09 18:30 Liverpool, UK
    # Sidereal Lahiri
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
    
    assert subject.vargas is not None
    assert "D9" in subject.vargas
    
    d9 = subject.vargas["D9"]
    
    # Check Moon in D9
    # Moon in Sidereal Lahiri: 10°51' Capricorn
    # Capricorn is Earthy. Start from Capricorn (9).
    # 10.51 / 3.333 = 3rd part (index 3)
    # 9, 10, 11, 0 (Aries)
    moon_d9 = d9.points["moon"]
    assert moon_d9.sign == "Ari"
    
    # Check Sun in D9
    # Sun in Sidereal Lahiri: 23°14' Virgo
    # Virgo is Earthy. Start from Capricorn (9).
    # 23.23 / 3.333 = 6th part (index 6)
    # 9, 10, 11, 0, 1, 2, 3 (Cancer)
    sun_d9 = d9.points["sun"]
    assert sun_d9.sign == "Can"
    
    # Check D2 (Hora)
    # Sun in Virgo (Even sign) at 23°14' (Second half > 15°)
    # Even sign Second half -> Leo (4)
    d2 = subject.vargas["D2"]
    sun_d2 = d2.points["sun"]
    assert sun_d2.sign == "Leo"
    
    # Check D3 (Drekkana)
    # Sun in Virgo at 23°14' (3rd decan)
    # Virgo (Earthy) + 8 signs = 5 (Vir) + 8 = 13 % 12 = 1 (Taurus)
    d3 = subject.vargas["D3"]
    sun_d3 = d3.points["sun"]
    assert sun_d3.sign == "Tau"
    
    # Enrichments (New in v5.13)
    assert sun_d9.dignity is not None
    assert sun_d9.sign_lord == "Moon" # Rulers of Cancer
    assert sun_d9.is_vargottama is False
    assert sun_d9.is_pushkara is False
    
    assert moon_d9.sign_lord == "Mars" # Rulers of Aries
    assert moon_d9.is_pushkara is False
    
    # Check Jupiter (Pushkara Bhaga check)
    # Jupiter in Sidereal Lahiri is at ~20°54' Aries (close to 21 Ari)
    # Aries (Fire 0) 21 Ari is in 7th Navamsha (index 6).
    # 20.9 / 3.33 = 6.27 -> index 6.
    # So it should be Pushkara!
    jupiter_d9 = d9.points["jupiter"]
    assert jupiter_d9.is_pushkara is True

if __name__ == "__main__":
    test_lennon_vargas()
    print("Varga tests passed!")
