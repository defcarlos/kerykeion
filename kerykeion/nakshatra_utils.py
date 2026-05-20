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
from kerykeion.schemas.kr_literals import Nakshatra, NakshatraLord, Gana, Nadi, NakshatraQuality


NAKSHATRA_NAMES: Tuple[Nakshatra, ...] = (
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
)

NAKSHATRA_LORDS: Tuple[NakshatraLord, ...] = (
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
)

NAKSHATRA_GANAS: Tuple[Gana, ...] = (
    "Deva", "Manushya", "Rakshasa", "Manushya", "Deva", "Manushya",
    "Deva", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya",
    "Deva", "Rakshasa", "Deva", "Rakshasa", "Deva", "Rakshasa",
    "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Rakshasa",
    "Manushya", "Manushya", "Deva",
)

NAKSHATRA_YONIS: Tuple[str, ...] = (
    "Horse (Male)", "Elephant (Female)", "Sheep (Female)", "Serpent (Male)", "Serpent (Female)", "Dog (Female)",
    "Cat (Female)", "Sheep (Male)", "Cat (Male)", "Rat (Male)", "Rat (Female)", "Cow (Female)",
    "Buffalo (Female)", "Tiger (Female)", "Buffalo (Male)", "Tiger (Male)", "Deer (Female)", "Deer (Male)",
    "Dog (Male)", "Monkey (Male)", "Mongoose (Male)", "Monkey (Female)", "Lion (Female)", "Horse (Female)",
    "Lion (Male)", "Cow (Male)", "Elephant (Male)",
)

NAKSHATRA_NADIS: Tuple[Nadi, ...] = (
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya",
)

NAKSHATRA_SYMBOLS: Tuple[str, ...] = (
    "Horse's Head", "Yoni / Vessel", "Knife / Razor", "Chariot / Temple", "Deer's Head", "Teardrop / Diamond",
    "Bow and Quiver", "Flower / Cow's Udder", "Coiled Serpent", "Royal Throne", "Front Legs of Bed", "Back Legs of Bed",
    "Hand / Palm", "Bright Jewel", "Coral / Sprout in Wind", "Triumphal Arch", "Lotus Flower", "Umbrella / Earring",
    "Bunch of Roots", "Winnowing Basket", "Elephant's Tusk", "Three Footprints / Ear", "Drum / Flute", "Empty Circle / 1000 Flowers",
    "Front Parts of Corpse", "Back Parts of Corpse", "Fish / Drum",
)

NAKSHATRA_QUALITIES: Tuple[NakshatraQuality, ...] = (
    "Kshipra", "Ugra", "Mishra", "Sthira", "Mridu", "Tikshna",
    "Chara", "Kshipra", "Tikshna", "Ugra", "Ugra", "Sthira",
    "Kshipra", "Mridu", "Chara", "Mishra", "Mridu", "Tikshna",
    "Tikshna", "Ugra", "Sthira", "Chara", "Chara", "Chara",
    "Ugra", "Sthira", "Mridu",
)

NAKSHATRA_DEITIES: Tuple[str, ...] = (
    "Aswini Kumara", "Yama", "Agni", "Bramha", "Moon", "Shiva",
    "Aditi", "Jupiter", "Rahu", "Sun", "Aryaman", "Sun",
    "Viswakarma", "Vaayu", "Indra", "Mitra", "Indra", "Nirriti",
    "Varuna", "Viswadeva", "Brahma", "Vishnu", "Vasu", "Varuna",
    "Ajacharana", "Ahirbudhanya", "Pooshan",
)


def get_nakshatra_data(abs_pos: float, ayanamsa: float = 0.0) -> Dict[str, Any]:
    """
    Calculate Nakshatra information for a given absolute zodiacal position.

    Args:
        abs_pos: Absolute position in the zodiac (0-360 degrees).
        ayanamsa: Ayanamsa offset in degrees to convert from Tropical to Sidereal.
            If the abs_pos is already sidereal, ayanamsa should be 0.0.

    Returns:
        A dictionary containing Nakshatra name, number, pada, lord, deity, and enhanced metadata.
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
        "nakshatra_gana": NAKSHATRA_GANAS[nakshatra_index],
        "nakshatra_yoni": NAKSHATRA_YONIS[nakshatra_index],
        "nakshatra_nadi": NAKSHATRA_NADIS[nakshatra_index],
        "nakshatra_symbol": NAKSHATRA_SYMBOLS[nakshatra_index],
        "nakshatra_quality": NAKSHATRA_QUALITIES[nakshatra_index],
    }
