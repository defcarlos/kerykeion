# -*- coding: utf-8 -*-
"""
Western Astrological Utilities
==============================

This module provides utility functions for Western (Ptolemaic) astrological 
calculations, including essential dignities (Domicile, Exaltation, Detriment, Fall).

This is part of Kerykeion (C) 2025 Giacomo Battaglia
"""

from typing import Optional, Dict, List
from kerykeion.schemas.kr_literals import WesternDignity

# Traditional Rulerships (Seven Planets)
WESTERN_DOMICILES: Dict[str, List[int]] = {
    "Sun": [4],        # Leo
    "Moon": [3],       # Cancer
    "Mercury": [2, 5], # Gemini, Virgo
    "Venus": [1, 6],   # Taurus, Libra
    "Mars": [0, 7],    # Aries, Scorpio
    "Jupiter": [8, 11],# Sagittarius, Pisces
    "Saturn": [9, 10], # Capricorn, Aquarius
}

# Traditional Exaltations/Falls
# (Planet: (Exaltation Sign, Fall Sign))
WESTERN_EXALTATIONS: Dict[str, tuple[int, int]] = {
    "Sun": (0, 6),     # Ex: Aries, Fall: Libra
    "Moon": (1, 7),    # Ex: Taurus, Fall: Scorpio
    "Mercury": (5, 11),# Ex: Virgo, Fall: Pisces
    "Venus": (11, 5),  # Ex: Pisces, Fall: Virgo
    "Mars": (9, 3),    # Ex: Capricorn, Fall: Cancer
    "Jupiter": (3, 9), # Ex: Cancer, Fall: Capricorn
    "Saturn": (6, 0),  # Ex: Libra, Fall: Aries
}

def get_western_sign_lord(sign_num: int) -> Optional[str]:
    """
    Returns the traditional ruler of a sign in Western astrology.
    """
    for planet, signs in WESTERN_DOMICILES.items():
        if sign_num in signs:
            return planet
    return None

def get_western_dignity(planet_name: str, sign_num: int) -> Optional[WesternDignity]:
    """
    Determine the essential dignity of a planet in a specific position (Western rules).
    
    Args:
        planet_name: Name of the planet (e.g., 'Sun').
        sign_num: Numerical identifier for the zodiac sign (0-11).
        
    Returns:
        The WesternDignity literal (e.g., 'Domicile', 'Detriment').
    """
    # Normalize name for lookup
    p_name = planet_name.capitalize()
    
    # 1. Check for Domicile
    if sign_num in WESTERN_DOMICILES.get(p_name, []):
        return "Domicile"
        
    # 2. Check for Detriment (Opposite of Domicile)
    # Detriment is always in the opposite sign (+6 mod 12)
    dom_signs = WESTERN_DOMICILES.get(p_name, [])
    det_signs = [(s + 6) % 12 for s in dom_signs]
    if sign_num in det_signs:
        return "Detriment"
        
    # 3. Check for Exaltation / Fall
    ex_fall = WESTERN_EXALTATIONS.get(p_name)
    if ex_fall:
        if sign_num == ex_fall[0]:
            return "Exaltation"
        if sign_num == ex_fall[1]:
            return "Fall"
            
    # 4. Peregrine (No essential dignity)
    # Only applicable to traditional planets in this basic model
    if p_name in WESTERN_DOMICILES:
        return "Peregrine"
        
    return None
