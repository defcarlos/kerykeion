# -*- coding: utf-8 -*-
"""
Vedic Astrological Utilities
============================

This module provides utility functions for Vedic astrological calculations,
including essential dignities, sign rulers, Pushkara degrees, and
interpretive Panchang metadata.

This is part of Kerykeion (C) 2025 Giacomo Battaglia
"""

from typing import Optional, Tuple, Dict, Any, List
from kerykeion.schemas.kr_literals import VedicDignity, Auspiciousness, Tithi, Yoga, Karana
from kerykeion.settings.vedic_constants import (
    PLANETARY_DOMICILES,
    EXALTATION_DEGREES,
    DEBILITATION_DEGREES,
    MOOLATRIKONA_RANGES,
    NATURAL_RELATIONSHIPS,
)


def get_sign_lord(sign_num: int) -> Optional[str]:
    """
    Returns the name of the traditional ruler of a zodiac sign.
    
    Args:
        sign_num: Numerical identifier for the zodiac sign (0-11).
        
    Returns:
        The name of the planet (e.g., 'Mars' for Aries).
    """
    for planet, signs in PLANETARY_DOMICILES.items():
        if sign_num in signs:
            return planet
    return None


def get_vedic_dignity(
    planet_name: str, 
    sign_num: int, 
    position: float, 
    temporary_friends: Optional[List[str]] = None
) -> Optional[VedicDignity]:
    """
    Determine the essential dignity of a planet in a specific position (Vedic rules).
    
    Args:
        planet_name: Name of the planet (e.g., 'Sun').
        sign_num: Numerical identifier for the zodiac sign (0-11).
        position: Position within the sign (0-30 degrees).
        temporary_friends: Optional list of temporary friends for combined relationship calculation.
        
    Returns:
        The VedicDignity literal (e.g., 'Exalted', 'Own Sign').
    """
    if planet_name not in EXALTATION_DEGREES and planet_name not in PLANETARY_DOMICILES:
        return None

    # 1. Check for Exaltation
    ex_sign, ex_deg = EXALTATION_DEGREES.get(planet_name, (-1, -1))
    if sign_num == ex_sign:
        # Classical definition: specific degree is peak, but usually whole sign is exalted
        # Kerykeion uses a 1-degree window for specific dignity checks in reports, 
        # but here we follow general Jyotish: if in sign, it is Exalted.
        return "Exalted"

    # 2. Check for Debilitation
    deb_sign, deb_deg = DEBILITATION_DEGREES.get(planet_name, (-1, -1))
    if sign_num == deb_sign:
        return "Debilitated"

    # 3. Check for Moolatrikona
    mt = MOOLATRIKONA_RANGES.get(planet_name)
    if mt and sign_num == mt[0] and mt[1] <= position <= mt[2]:
        return "Moolatrikona"

    # 4. Check for Own Sign
    if sign_num in PLANETARY_DOMICILES.get(planet_name, []):
        return "Own Sign"

    # 5. Friendship (Natural + Temporary)
    ruler = get_sign_lord(sign_num)
    if not ruler or ruler == planet_name:
        return "Neutral"

    natural_rel = NATURAL_RELATIONSHIPS.get(planet_name, {}).get(ruler, 0)
    
    # If temporary friends are provided, calculate combined relationship
    if temporary_friends is not None:
        temp_rel = 1 if ruler in temporary_friends else -1
        combined = natural_rel + temp_rel
        
        if combined >= 2: return "Great Friend"
        if combined == 1: return "Friend"
        if combined == -1: return "Enemy"
        if combined <= -2: return "Great Enemy"
        return "Neutral"
    
    # Otherwise return natural relationship
    if natural_rel == 1: return "Friend"
    if natural_rel == -1: return "Enemy"
    
    return "Neutral"


def is_pushkara(sign_num: int, position: float, varga_type: str = "D1") -> bool:
    """
    Check if a point falls in a Pushkara Navamsha or Pushkara Bhaga.
    
    Pushkara Navamshas are specific auspicious degrees across the zodiac.
    
    Args:
        sign_num: Numerical identifier for the zodiac sign (0-11).
        position: Position within the sign (0-30 degrees).
        varga_type: The varga context (logic primarily applies to D1 and D9).
        
    Returns:
        True if the point is in a Pushkara degree/navamsha.
    """
    # 1. Pushkara Bhaga (Specific auspicious degrees)
    # Degrees: Ari 21, Tau 14, Gem 24, Can 7, Leo 21, Vir 14, Lib 24, Sco 7, Sag 21, Cap 14, Aqu 24, Pis 7
    bhaga_degrees = {0: 21, 1: 14, 2: 24, 3: 7, 4: 21, 5: 14, 6: 24, 7: 7, 8: 21, 9: 14, 10: 24, 11: 7}
    
    # Check within 1 degree window for Bhaga
    if abs(position - bhaga_degrees.get(sign_num, -100)) <= 1.0:
        return True

    # 2. Pushkara Navamsha (Auspicious Navamsha sections)
    # Navamshas are 3°20' wide.
    # Fire Signs (0, 4, 8): 7th (20-23.20) and 9th (26.40-30)
    # Earth Signs (1, 5, 9): 3rd (6.40-10) and 5th (13.20-16.40)
    # Air Signs (2, 6, 10): 6th (16.40-20) and 8th (23.20-26.40)
    # Water Signs (3, 7, 11): 1st (0-3.20) and 3rd (6.40-10)
    
    element_num = sign_num % 4 # 0=Fire, 1=Earth, 2=Air, 3=Water
    nav_index = int(position / (30/9)) # 0 to 8
    
    if element_num == 0: # Fire
        if nav_index in [6, 8]: return True
    elif element_num == 1: # Earth
        if nav_index in [2, 4]: return True
    elif element_num == 2: # Air
        if nav_index in [5, 7]: return True
    elif element_num == 3: # Water
        if nav_index in [0, 2]: return True
        
    return False


def get_tithi_metadata(name: Tithi, paksha: str) -> Dict[str, Any]:
    """
    Returns interpretive metadata for a Tithi.
    """
    # Tithi Rulers: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu (Repeat)
    rulers = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]
    
    # Tithi list for index lookup
    tithis = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti", 
        "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", 
        "Trayodashi", "Chaturdashi", "Purnima" # Amavasya is special
    ]
    
    try:
        if name == "Amavasya":
            index = 14
        else:
            index = tithis.index(name)
    except ValueError:
        index = 0
        
    ruler = rulers[index % 8]
    
    # Auspiciousness (Basic)
    # Auspicious: 2, 3, 5, 7, 10, 11, 13
    # Inauspicious: 4, 9, 14, Amavasya
    auspicious = [1, 2, 4, 6, 9, 10, 12] # 0-indexed: 2, 3, 5, 7, 10, 11, 13
    inauspicious = [3, 8, 13, 14] # 4, 9, 14, Amavasya
    
    status: Auspiciousness = "Neutral"
    if index in auspicious: status = "Auspicious"
    elif index in inauspicious: status = "Inauspicious"
    
    return {
        "planetary_ruler": ruler,
        "status": status
    }


def get_yoga_metadata(name: Yoga) -> Dict[str, Any]:
    """
    Returns interpretive metadata for a Yoga.
    """
    # Standard Nitya Yoga rulers follow the Nakshatra sequence starting from Ketu
    rulers = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    
    yogas = [
        "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Sobhana", "Atiganda", 
        "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", 
        "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva", 
        "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
    ]
    
    try:
        index = yogas.index(name)
    except ValueError:
        index = 0
        
    ruler = rulers[index % 9]
    
    # Malefic Yogas (Inauspicious)
    malefic = [0, 5, 8, 9, 12, 14, 16, 18, 26] # Vishkumbha, Atiganda, Shula, Ganda, Vyaghata, Vajra, Vyatipata, Parigha, Vaidhriti
    
    status: Auspiciousness = "Auspicious"
    if index in malefic:
        status = "Inauspicious"
        
    return {
        "planetary_ruler": ruler,
        "status": status
    }


def get_karana_metadata(name: Karana) -> Dict[str, Any]:
    """
    Returns interpretive metadata for a Karana.
    """
    # Karana Rulers
    rulers_map = {
        "Bava": "Sun", "Balava": "Moon", "Kaulava": "Mars", "Taitila": "Mercury",
        "Gara": "Jupiter", "Vanija": "Venus", "Vishti": "Saturn",
        "Shakuni": "Rahu", "Chatushpada": "Ketu", "Naga": "Mars", "Kimstughna": "Jupiter"
    }
    
    ruler = rulers_map.get(name, "Unknown")
    
    # Vishti (Bhadra) is famously inauspicious
    status: Auspiciousness = "Auspicious"
    if name == "Vishti":
        status = "Inauspicious"
    elif name in ["Shakuni", "Chatushpada", "Naga"]:
        status = "Mixed"
        
    return {
        "planetary_ruler": ruler,
        "status": status
    }
