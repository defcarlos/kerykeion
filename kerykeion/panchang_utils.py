# -*- coding: utf-8 -*-
"""
Panchang Utilities
==================

This module provides utility functions for calculating the Panchang (Five Limbs),
which are essential components of Vedic time-keeping:
1. Tithi (Lunar Day)
2. Nakshatra (Lunar Mansion) - Reused from nakshatra_utils
3. Vara (Weekday)
4. Yoga (Luni-Solar Day)
5. Karana (Half-Tithi)

Calculations are based on the angular relationship between the Sun and Moon.
"""

from typing import Dict, Any, Tuple, Optional
from kerykeion.schemas.kr_literals import Tithi, Paksha, Yoga, Karana, Nakshatra, NakshatraLord

# --- Data Tables ---

TITHI_LIST: Tuple[Tithi, ...] = (
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashti",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Amavasya"
)

TITHI_DEITIES: Tuple[str, ...] = (
    "Agni", "Brahma", "Gauri", "Ganapati", "Naga", "Kartikeya",
    "Surya", "Shiva", "Durga", "Yama", "Viswedevas", "Vishnu",
    "Kama", "Shiva", "Moon",  # Shukla
    "Agni", "Brahma", "Gauri", "Ganapati", "Naga", "Kartikeya",
    "Surya", "Shiva", "Durga", "Yama", "Viswedevas", "Vishnu",
    "Kama", "Shiva", "Pitris"  # Krishna
)

YOGA_NAMES: Tuple[Yoga, ...] = (
    "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Sobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha",
    "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
)

YOGA_DEITIES: Tuple[str, ...] = (
    "Yama", "Vishnu", "Moon", "Brahma", "Brihaspati", "Moon", "Indra",
    "Apah", "Sarpa", "Agni", "Surya", "Prithvi", "Vaayu", "Bhaga",
    "Varuna", "Ganesha", "Rudra", "Kubera", "Vishwakarma", "Mitra",
    "Kartikeya", "Savitri", "Lakshmi", "Parvati", "Dharma", "Pitris", "Aditi"
)

KARANA_NAMES: Tuple[Karana, ...] = (
    "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna"
)

KARANA_DEITIES: Tuple[str, ...] = (
    "Indra", "Brahma", "Mitra", "Aryaman", "Bhaga", "Manibhadra", "Yama",
    "Kali", "Rudra", "Sarpa", "Vayu"
)

# --- Logic ---

def get_tithi_data(moon_abs_pos: float, sun_abs_pos: float) -> Dict[str, Any]:
    """
    Calculate Tithi (Lunar Day) from Sun and Moon positions.
    One Tithi is 12 degrees of separation.

    Returns:
        Dictionary with number (1-30), name, paksha, deity.
    """
    diff = (moon_abs_pos - sun_abs_pos) % 360.0
    tithi_number = int(diff / 12.0) + 1
    tithi_number = min(max(1, tithi_number), 30)

    paksha: Paksha = "Shukla" if tithi_number <= 15 else "Krishna"
    
    return {
        "number": tithi_number,
        "name": TITHI_LIST[tithi_number - 1],
        "paksha": paksha,
        "deity": TITHI_DEITIES[tithi_number - 1]
    }

def get_yoga_data(moon_abs_pos: float, sun_abs_pos: float) -> Dict[str, Any]:
    """
    Calculate Nitya Yoga (Sun + Moon) from positions.
    One Yoga is 13°20' (the same width as a Nakshatra).
    """
    # Yoga is (Sun + Moon) / 13°20'
    combined = (sun_abs_pos + moon_abs_pos) % 360.0
    yoga_width = 360.0 / 27.0
    yoga_index = int(combined / yoga_width)
    yoga_index = min(max(0, yoga_index), 26)

    return {
        "number": yoga_index + 1,
        "name": YOGA_NAMES[yoga_index],
        "deity": YOGA_DEITIES[yoga_index]
    }

def get_karana_data(moon_abs_pos: float, sun_abs_pos: float) -> Dict[str, Any]:
    """
    Calculate Karana (Half-Tithi) from Sun and Moon positions.
    One Karana is 6 degrees of separation.
    
    Karanas are more complex as they follow a cyclic pattern of 7 movable 
    karanas and 4 fixed ones.
    """
    diff = (moon_abs_pos - sun_abs_pos) % 360.0
    total_karanas = int(diff / 6.0) # 0 to 59
    
    # Karana 1 is Kimstughna (Fixed) - always the first half of the first Tithi
    if total_karanas == 0:
        k_index = 10 # Kimstughna
    # Last 3 half-tithis are fixed: Shakuni, Chatushpada, Naga
    elif total_karanas == 57:
        k_index = 7 # Shakuni
    elif total_karanas == 58:
        k_index = 8 # Chatushpada
    elif total_karanas == 59:
        k_index = 9 # Naga
    else:
        # Movable karananas (Bava to Vishti) cycle 8 times
        # The first movable karana (Bava) starts at the second half of the first Tithi (total_karanas == 1)
        k_index = (total_karanas - 1) % 7
        
    return {
        "number": k_index + 1,
        "name": KARANA_NAMES[k_index],
        "deity": KARANA_DEITIES[k_index]
    }
