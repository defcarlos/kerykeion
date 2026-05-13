# -*- coding: utf-8 -*-
import unittest
from kerykeion import AstrologicalSubjectFactory
from kerykeion.nakshatra_utils import get_nakshatra_data

class TestNakshatras(unittest.TestCase):
    def test_core_math(self):
        # 0 Sidereal Aries = Ashwini Pada 1, Ketu lord
        data = get_nakshatra_data(0.0, 0.0)
        self.assertEqual(data["nakshatra"], "Ashwini")
        self.assertEqual(data["nakshatra_number"], 1)
        self.assertEqual(data["nakshatra_pada"], 1)
        self.assertEqual(data["nakshatra_lord"], "Ketu")

        # 13°20' Sidereal Aries = Bharani Pada 1, Venus lord
        data = get_nakshatra_data(13.333333333333334, 0.0)
        self.assertEqual(data["nakshatra"], "Bharani")
        self.assertEqual(data["nakshatra_pada"], 1)
        self.assertEqual(data["nakshatra_lord"], "Venus")

        # 3°20' Sidereal Aries = Ashwini Pada 2
        data = get_nakshatra_data(3.3333333333333335, 0.0)
        self.assertEqual(data["nakshatra_pada"], 2)

    def test_hybrid_tropical_chart(self):
        # Create a Tropical chart for a fixed time
        # 2024-01-01 00:00 UTC at 0,0
        # Ayanamsa Lahiri for this date is ~24.18 degrees
        # Tropical Sun is at ~280.22 (10° Capricorn)
        # Sidereal Sun (Lahiri) is at ~256.04 (16° Sagittarius)
        # 256.04 / 13.333 = 19.2 Nakshatra index -> 20th Nakshatra (Purva Ashadha)
        
        subject = AstrologicalSubjectFactory.from_birth_data(
            name="Hybrid Test",
            year=2024, month=1, day=1,
            hour=0, minute=0,
            lng=0.0, lat=0.0, tz_str="Etc/GMT",
            online=False,
            zodiac_type="Tropical",
            nakshatra_ayanamsa="LAHIRI"
        )
        
        # Verify zodiac is tropical
        self.assertEqual(subject.zodiac_type, "Tropical")
        # 2024-01-01 00:00:00 UTC Sun is at approx 280.04
        self.assertAlmostEqual(subject.sun.abs_pos, 280.04, places=1)
        
        # Verify Nakshatra is sidereal
        # Sidereal pos ≈ 280.04 - 24.19 ≈ 255.85 -> Purva Ashadha
        self.assertEqual(subject.sun.nakshatra, "Purva Ashadha")
        self.assertEqual(subject.sun.nakshatra_number, 20)
        self.assertEqual(subject.sun.nakshatra_lord, "Venus")

    def test_sidereal_chart(self):
        # Create a Sidereal chart (Lahiri)
        subject = AstrologicalSubjectFactory.from_birth_data(
            name="Sidereal Test",
            year=2024, month=1, day=1,
            hour=0, minute=0,
            lng=0.0, lat=0.0, tz_str="Etc/GMT",
            online=False,
            zodiac_type="Sidereal",
            sidereal_mode="LAHIRI"
        )
        
        # In sidereal charts, the abs_pos is already sidereal.
        # Offset should be 0 for Nakshatra calculation.
        self.assertEqual(subject.zodiac_type, "Sidereal")
        self.assertAlmostEqual(subject.sun.abs_pos, 255.85, places=1)
        
        # Should match the hybrid calculation above
        self.assertEqual(subject.sun.nakshatra, "Purva Ashadha")

    def test_custom_nakshatra_ayanamsa(self):
        # Use a different ayanamsa for Nakshatras
        subject = AstrologicalSubjectFactory.from_birth_data(
            name="Custom Nakshatra Ayanamsa",
            year=2024, month=1, day=1,
            hour=0, minute=0,
            lng=0.0, lat=0.0, tz_str="Etc/GMT",
            online=False,
            zodiac_type="Tropical",
            nakshatra_ayanamsa="FAGAN_BRADLEY"
        )
        
        # Fagan-Bradley is ~1 degree ahead of Lahiri
        # Sidereal Sun would be ~255.1 instead of 256.0
        # Still Purva Ashadha but different pada/exact pos
        self.assertEqual(subject.sun.nakshatra, "Purva Ashadha")

if __name__ == "__main__":
    unittest.main()
