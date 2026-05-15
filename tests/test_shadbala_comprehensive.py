# -*- coding: utf-8 -*-
"""
Comprehensive Tests for Shadbala Calculations.
"""

from kerykeion import AstrologicalSubjectFactory
import pytest

def test_shadbala_components():
    # John Lennon, 1940-10-09 18:30 Liverpool, UK
    # Sidereal Lahiri
    # Night birth (Sun below horizon)
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
    
    assert subject.shadbala is not None
    s = subject.shadbala
    
    print("\n" + "="*50)
    print(f" SHADBALA TEST: {subject.name} ")
    print("="*50)
    print(f"{'Planet':<10} | {'Sthana':<7} | {'Dig':<7} | {'Kala':<7} | {'Chesta':<7} | {'Nais':<7} | {'Drik':<7} | {'Total'}")
    print("-" * 75)
    
    planets = ["sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn"]
    for p in planets:
        b = s[p]
        print(f"{p:<10} | {b.sthana_bala:<7} | {b.dig_bala:<7} | {b.kala_bala:<7} | {b.chesta_bala:<7} | {b.naisargika_bala:<7} | {b.drik_bala:<7} | {b.total_virupas}")

    # 1. Test Naisargika (Fixed values)
    assert s.sun.naisargika_bala == 60.0
    assert s.saturn.naisargika_bala == 8.57
    
    # 2. Test Dig Bala (Directional)
    # Jupiter is in Aries (D1) in the 1st house for Lennon (near Ascendant)
    # Jupiter max is 1st house. 
    # Should be high (near 60)
    assert s.jupiter.dig_bala > 50.0
    
    # 3. Test Kala Bala (Nathonnatha - Sect)
    # Lennon is a Night birth. 
    # Moon, Mars, Saturn should have 60 from Nathonnatha.
    # We also have Paksha Bala now.
    assert s.moon.kala_bala > 60.0 # Nathonnatha(60) + Paksha
    
    # 4. Test Chesta Bala (Motional)
    # Jupiter was retrograde on Lennon's birth
    assert s.jupiter.chesta_bala == 60.0
    # Sun and Moon always 0
    assert s.sun.chesta_bala == 0.0
    assert s.moon.chesta_bala == 0.0

def test_day_birth_kala():
    # Day birth: Sun at noon
    subject = AstrologicalSubjectFactory.from_birth_data(
        name="Day Test",
        year=2024, month=6, day=1, hour=12, minute=0,
        city="London", nation="GB", online=False,
        lng=0, lat=51.5, tz_str="UTC",
        zodiac_type="Tropical"
    )
    
    assert subject.is_diurnal is True
    s = subject.shadbala
    # With advanced components (Ayana, Dina, Hora, etc.), Kala Bala values are higher.
    # Sun, Jupiter, Venus are strong (diurnal)
    assert s.sun.kala_bala > 150.0
    assert s.jupiter.kala_bala > 100.0
    assert s.venus.kala_bala > 150.0
    # Moon, Mars, Saturn are weak (diurnal) but still have Paksha/Ayana/Lords
    assert s.moon.kala_bala > 60.0
    assert s.mars.kala_bala > 70.0
    assert s.saturn.kala_bala > 70.0

if __name__ == "__main__":
    test_shadbala_components()
    test_day_birth_kala()
    print("\nAll Shadbala verification tests passed!")
