# -*- coding: utf-8 -*-
"""
Vedic Astrological Constants
============================

This module contains fixed data tables and constants required for Vedic
astrological calculations, including Shadbala and Essential Dignities.

Includes:
- Exaltation and Debilitation degrees
- Moolatrikona ranges
- Natural Relationships (Naisargika Maitri)
- Natural Strengths (Naisargika Bala)
- Dig Bala zero-points

This is part of Kerykeion (C) 2025 Giacomo Battaglia
"""

# Exaltation Degrees (Parashari)
# Maps planet to (Sign Number, Degree in Sign)
EXALTATION_DEGREES = {
    "Sun": (0, 10),      # Aries 10°
    "Moon": (1, 3),      # Taurus 3°
    "Mars": (9, 28),     # Capricorn 28°
    "Mercury": (5, 15),  # Virgo 15°
    "Jupiter": (3, 5),   # Cancer 5°
    "Venus": (11, 27),   # Pisces 27°
    "Saturn": (6, 20),   # Libra 20°
}

# Debilitation is exactly 180° from Exaltation
DEBILITATION_DEGREES = {
    p: ((sign + 6) % 12, deg) for p, (sign, deg) in EXALTATION_DEGREES.items()
}

# Moolatrikona Ranges
# Maps planet to (Sign Number, Start Degree, End Degree)
MOOLATRIKONA_RANGES = {
    "Sun": (0, 0, 20),      # Aries 0-20°
    "Moon": (1, 4, 30),     # Taurus 4-30°
    "Mars": (0, 0, 12),     # Aries 0-12° (Some sources say 0-12)
    "Mercury": (5, 16, 20), # Virgo 16-20°
    "Jupiter": (8, 0, 10),  # Sagittarius 0-10°
    "Venus": (6, 0, 15),    # Libra 0-15°
    "Saturn": (10, 0, 20),  # Aquarius 0-20°
}

# Natural Rulerships (Domicile)
PLANETARY_DOMICILES = {
    "Sun": [4],             # Leo
    "Moon": [3],            # Cancer
    "Mars": [0, 7],         # Aries, Scorpio
    "Mercury": [1, 5],      # Gemini, Virgo
    "Jupiter": [8, 11],     # Sagittarius, Pisces
    "Venus": [1, 6],        # Taurus, Libra
    "Saturn": [9, 10],      # Capricorn, Aquarius
}

# Natural Relationships (Naisargika Maitri)
# 1 = Friend, 0 = Neutral, -1 = Enemy
NATURAL_RELATIONSHIPS = {
    "Sun": {"Moon": 1, "Mars": 1, "Mercury": 0, "Jupiter": 1, "Venus": -1, "Saturn": -1},
    "Moon": {"Sun": 1, "Mars": 0, "Mercury": 1, "Jupiter": 0, "Venus": 0, "Saturn": 0},
    "Mars": {"Sun": 1, "Moon": 1, "Mercury": -1, "Jupiter": 1, "Venus": 0, "Saturn": 0},
    "Mercury": {"Sun": 1, "Moon": -1, "Mars": 0, "Jupiter": 0, "Venus": 1, "Saturn": 0},
    "Jupiter": {"Sun": 1, "Moon": 1, "Mars": 1, "Mercury": -1, "Venus": -1, "Saturn": 0},
    "Venus": {"Sun": -1, "Moon": -1, "Mars": 0, "Jupiter": 0, "Mercury": 1, "Saturn": 1},
    "Saturn": {"Sun": -1, "Moon": -1, "Mars": -1, "Jupiter": 0, "Mercury": 1, "Venus": 1},
}

# Natural Strength (Naisargika Bala) in Virupas
# Sun is strongest, Saturn weakest.
NAISARGIKA_BALA_VALUES = {
    "Sun": 60.00,
    "Moon": 51.43,
    "Mars": 17.14,
    "Mercury": 25.71,
    "Jupiter": 34.28,
    "Venus": 42.85,
    "Saturn": 8.57,
}

# Dig Bala (Directional Strength) Max Points Locations
# Maps planet to the House number where it gets 60 Virupas
DIG_BALA_MAX_POINTS = {
    "Sun": 10,      # South (MC)
    "Mars": 10,     # South (MC)
    "Moon": 4,      # North (IC)
    "Venus": 4,     # North (IC)
    "Jupiter": 1,   # East (Asc)
    "Mercury": 1,   # East (Asc)
    "Saturn": 7,    # West (Desc)
}

# Saptavarga Strength Weights (in Virupas)
# For Sthana Bala calculations
SAPTAVARGA_WEIGHTS = {
    "Exaltation": 60,
    "Moolatrikona": 45,
    "Own_Sign": 30,
    "Great_Friend": 22.5,
    "Friend": 15,
    "Neutral": 7.5,
    "Enemy": 3.75,
    "Great_Enemy": 1.875,
    "Debilitation": 0,
}

# Shadbala Minimum Strength Requirements (in Rupas)
# Standard Parashari thresholds
SHADBALA_MINIMUM_REQUIREMENTS = {
    "Sun": 6.5,
    "Moon": 6.0,
    "Mars": 5.0,
    "Mercury": 7.0,
    "Jupiter": 6.5,
    "Venus": 5.5,
    "Saturn": 5.0,
}
