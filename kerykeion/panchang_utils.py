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

import swisseph as swe
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional, Callable
from kerykeion.schemas.kr_literals import Tithi, Paksha, Yoga, Karana, Nakshatra, NakshatraLord

# --- Data Tables ---
# ... (existing tables)

# --- Logic ---

def _get_abs_pos(jd: float, planet: int) -> float:
    """Helper to get absolute position of a planet at a Julian Day."""
    res = swe.calc_ut(jd, planet)[0]
    return float(res[0])

def _find_boundary(
    jd: float, 
    func: Callable[[float], float], 
    target_val: float, 
    search_range: float = 1.0, 
    precision: float = 0.00001
) -> float:
    """
    Find the exact Julian Day when func(jd) crosses target_val.
    Uses bisection with boundary crossing detection.
    """
    low = jd - search_range
    high = jd + search_range
    
    # Refine the window to ensure it brackets the crossing
    # Step through the range to find where (func - target) changes sign
    steps = 24
    step_size = (high - low) / steps
    bracket_low = low
    bracket_high = high
    
    found = False
    v_low = (func(low) - target_val + 180) % 360 - 180
    for i in range(steps + 1):
        curr_jd = low + i * step_size
        v_curr = (func(curr_jd) - target_val + 180) % 360 - 180
        if v_low * v_curr <= 0:
            bracket_low = curr_jd - step_size
            bracket_high = curr_jd
            found = True
            break
        v_low = v_curr
        
    if not found:
        return jd # Fallback

    # Bisection on the bracket
    for _ in range(30): 
        mid = (bracket_low + bracket_high) / 2
        v_mid = (func(mid) - target_val + 180) % 360 - 180
        if v_low * v_mid <= 0:
            bracket_high = mid
        else:
            bracket_low = mid
            v_low = v_mid
            
    return (bracket_low + bracket_high) / 2

def _jd_to_iso(jd: float) -> str:
    """Convert Julian Day to ISO UTC string."""
    y, m, d, h = swe.revjul(jd)
    # revjul returns hour as float, need to split into h, m, s, ms
    hours = int(h)
    minutes = int((h - hours) * 60)
    seconds = int(((h - hours) * 60 - minutes) * 60)
    micro = int((((h - hours) * 60 - minutes) * 60 - seconds) * 1000000)
    dt = datetime(y, m, d, hours, minutes, seconds, micro, tzinfo=timezone.utc)
    return dt.isoformat()

def get_tithi_boundary(jd: float, direction: int) -> float:
    """Find the next (1) or previous (-1) Tithi boundary."""
    def tithi_diff(t_jd: float) -> float:
        m = _get_abs_pos(t_jd, swe.MOON)
        s = _get_abs_pos(t_jd, swe.SUN)
        return (m - s) % 360.0

    current_val = tithi_diff(jd)
    current_tithi_idx = int(current_val / 12.0)
    
    if direction > 0:
        target = (current_tithi_idx + 1) * 12.0
    else:
        target = current_tithi_idx * 12.0
        
    # Search window of ~1.5 days should cover any tithi transition
    return _find_boundary(jd, tithi_diff, target, search_range=1.5)

def get_nakshatra_boundary(jd: float, direction: int) -> float:
    """Find the next (1) or previous (-1) Nakshatra boundary."""
    def nak_pos(t_jd: float) -> float:
        return _get_abs_pos(t_jd, swe.MOON)

    yoga_width = 360.0 / 27.0
    current_val = nak_pos(jd)
    current_idx = int(current_val / yoga_width)
    
    if direction > 0:
        target = (current_idx + 1) * yoga_width
    else:
        target = current_idx * yoga_width
        
    return _find_boundary(jd, nak_pos, target, search_range=1.5)

def get_yoga_boundary(jd: float, direction: int) -> float:
    """Find the next (1) or previous (-1) Yoga boundary."""
    def yoga_pos(t_jd: float) -> float:
        m = _get_abs_pos(t_jd, swe.MOON)
        s = _get_abs_pos(t_jd, swe.SUN)
        return (m + s) % 360.0

    yoga_width = 360.0 / 27.0
    current_val = yoga_pos(jd)
    current_idx = int(current_val / yoga_width)
    
    if direction > 0:
        target = (current_idx + 1) * yoga_width
    else:
        target = current_idx * yoga_width
        
    return _find_boundary(jd, yoga_pos, target, search_range=1.5)

def get_karana_boundary(jd: float, direction: int) -> float:
    """Find the next (1) or previous (-1) Karana boundary."""
    def karana_diff(t_jd: float) -> float:
        m = _get_abs_pos(t_jd, swe.MOON)
        s = _get_abs_pos(t_jd, swe.SUN)
        return (m - s) % 360.0

    current_val = karana_diff(jd)
    current_karana_idx = int(current_val / 6.0)
    
    if direction > 0:
        target = (current_karana_idx + 1) * 6.0
    else:
        target = current_karana_idx * 6.0
        
    return _find_boundary(jd, karana_diff, target, search_range=0.8)

def get_sunrise_sunset(jd: float, lat: float, lng: float, alt: float = 0) -> Tuple[float, float]:
    """Calculate the sunrise and sunset for a given Julian Day and location."""
    # swe.rise_trans(jd_ut, planet, rsmi, geopos, atpress, attemp, flags)
    # rsmi: 1=rise, 2=set
    res_rise = swe.rise_trans(jd, swe.SUN, 1, (lng, lat, alt), 0, 0, swe.FLG_SWIEPH)[1][0]
    res_set = swe.rise_trans(jd, swe.SUN, 2, (lng, lat, alt), 0, 0, swe.FLG_SWIEPH)[1][0]
    return float(res_rise), float(res_set)

def get_tithi_data(moon_abs_pos: float, sun_abs_pos: float, jd: Optional[float] = None) -> Dict[str, Any]:
    """
    Calculate Tithi (Lunar Day) from Sun and Moon positions.
    One Tithi is 12 degrees of separation.
    """
    diff = (moon_abs_pos - sun_abs_pos) % 360.0
    tithi_number = int(diff / 12.0) + 1
    tithi_number = min(max(1, tithi_number), 30)

    paksha: Paksha = "Shukla" if tithi_number <= 15 else "Krishna"
    
    data = {
        "number": tithi_number,
        "name": TITHI_LIST[tithi_number - 1],
        "paksha": paksha,
        "deity": TITHI_DEITIES[tithi_number - 1],
        "start_time": None,
        "end_time": None
    }

    if jd is not None:
        data["start_time"] = _jd_to_iso(get_tithi_boundary(jd, -1))
        data["end_time"] = _jd_to_iso(get_tithi_boundary(jd, 1))

    return data

def get_yoga_data(moon_abs_pos: float, sun_abs_pos: float, jd: Optional[float] = None) -> Dict[str, Any]:
    """
    Calculate Nitya Yoga (Sun + Moon) from positions.
    """
    combined = (sun_abs_pos + moon_abs_pos) % 360.0
    yoga_width = 360.0 / 27.0
    yoga_index = int(combined / yoga_width)
    yoga_index = min(max(0, yoga_index), 26)

    data = {
        "number": yoga_index + 1,
        "name": YOGA_NAMES[yoga_index],
        "deity": YOGA_DEITIES[yoga_index],
        "start_time": None,
        "end_time": None
    }

    if jd is not None:
        data["start_time"] = _jd_to_iso(get_yoga_boundary(jd, -1))
        data["end_time"] = _jd_to_iso(get_yoga_boundary(jd, 1))

    return data

def get_karana_data(moon_abs_pos: float, sun_abs_pos: float, jd: Optional[float] = None) -> Dict[str, Any]:
    """
    Calculate Karana (Half-Tithi) from Sun and Moon positions.
    """
    diff = (moon_abs_pos - sun_abs_pos) % 360.0
    total_karanas = int(diff / 6.0) 
    
    if total_karanas == 0:
        k_index = 10 
    elif total_karanas == 57:
        k_index = 7 
    elif total_karanas == 58:
        k_index = 8 
    elif total_karanas == 59:
        k_index = 9 
    else:
        k_index = (total_karanas - 1) % 7
        
    data = {
        "number": k_index + 1,
        "name": KARANA_NAMES[k_index],
        "deity": KARANA_DEITIES[k_index],
        "start_time": None,
        "end_time": None
    }

    if jd is not None:
        data["start_time"] = _jd_to_iso(get_karana_boundary(jd, -1))
        data["end_time"] = _jd_to_iso(get_karana_boundary(jd, 1))

    return data
