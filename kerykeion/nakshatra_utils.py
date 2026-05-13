# -*- coding: utf-8 -*-
"""
Nakshatra Utilities

This module provides utility functions for calculating Nakshatras (Lunar Mansions),
their Padas (quarters), and Vimsottari Dasha lords from zodiacal positions.

The Nakshatra system divides the 360° zodiac into 27 equal segments of 13°20' each,
starting from 0° Sidereal Aries. Each Nakshatra is further divided into 4 Padas
of 3°20' each.

This is part of Kerykeion (C) 2025 Giacomo Battaglia
"""

from typing import Dict, Any, Tuple
from kerykeion.schemas.kr_literals import Nakshatra, NakshatraLord


NAKSHATRA_NAMES: Tuple[Nakshatra, ...] = (
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
)

NAKSHATRA_LORDS: Tuple[NakshatraLord, ...] = (
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
)

NAKSHATRA_DEITIES: Tuple[str, ...] = (
    "Aswini Kumara",
    "Yama",
    "Agni",
    "Bramha",
    "Moon",
    "Shiva",
    "Aditi",
    "Jupiter",
    "Rahu",
    "Sun",
    "Aryaman",
    "Sun",
    "Viswakarma",
    "Vaayu",
    "Indra",
    "Mitra",
    "Indra",
    "Nirriti",
    "Varuna",
    "Viswadeva",
    "Brahma",
    "Vishnu",
    "Vasu",
    "Varuna",
    "Ajacharana",
    "Ahirbudhanya",
    "Pooshan",
)


def get_nakshatra_data(abs_pos: float, ayanamsa: float = 0.0) -> Dict[str, Any]:
    """
    Calculate Nakshatra information for a given absolute zodiacal position.

    Args:
        abs_pos: Absolute position in the zodiac (0-360 degrees).
        ayanamsa: Ayanamsa offset in degrees to convert from Tropical to Sidereal.
            If the abs_pos is already sidereal, ayanamsa should be 0.0.

    Returns:
        A dictionary containing:
            - nakshatra: Name of the Nakshatra.
            - nakshatra_number: Numerical identifier (1-27).
            - nakshatra_pada: Pada number (1-4).
            - nakshatra_lord: Name of the Vimsottari Dasha lord.
            - nakshatra_deity: Ruling deity of the Nakshatra.
    """
    # Convert to sidereal position
    sidereal_pos = (abs_pos - ayanamsa) % 360.0

    # Each Nakshatra is 13°20' = 13.333333333333334 degrees
    nakshatra_width = 360.0 / 27.0
    
    # Each Pada is 3°20' = 3.3333333333333335 degrees
    pada_width = nakshatra_width / 4.0

    # Calculate indices
    nakshatra_index = int(sidereal_pos / nakshatra_width)
    # Ensure it stays within bounds 0-26 (handles floating point edge cases at 360.0)
    nakshatra_index = min(max(0, nakshatra_index), 26)

    remainder = sidereal_pos % nakshatra_width
    pada_index = int(remainder / pada_width)
    # Ensure it stays within bounds 0-3
    pada_index = min(max(0, pada_index), 3)

    # Dasha lords cycle every 9 Nakshatras
    lord_index = nakshatra_index % 9

    return {
        "nakshatra": NAKSHATRA_NAMES[nakshatra_index],
        "nakshatra_number": nakshatra_index + 1,
        "nakshatra_pada": pada_index + 1,
        "nakshatra_lord": NAKSHATRA_LORDS[lord_index],
        "nakshatra_deity": NAKSHATRA_DEITIES[nakshatra_index],
    }
