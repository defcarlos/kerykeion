# -*- coding: utf-8 -*-
"""
Shadbala (Six-fold Strength) Factory
====================================

This module provides the ShadbalaFactory class for calculating the six
traditional planetary strengths (Shadbala) according to Parashari rules.

Six Balas:
1. Sthana Bala (Positional Strength)
2. Dig Bala (Directional Strength)
3. Kala Bala (Temporal Strength)
4. Chesta Bala (Motional Strength)
5. Naisargika Bala (Natural Strength)
6. Drik Bala (Aspectual Strength)

This is part of Kerykeion (C) 2025 Giacomo Battaglia
"""

import logging
from typing import Dict, List, Optional, Union, Tuple

from kerykeion.schemas import (
    AstrologicalSubjectModel,
    ShadbalaModel,
    PlanetaryShadbalaModel,
    KerykeionPointModel,
)
from kerykeion.settings.vedic_constants import (
    NAISARGIKA_BALA_VALUES,
    DIG_BALA_MAX_POINTS,
    EXALTATION_DEGREES,
    DEBILITATION_DEGREES,
    MOOLATRIKONA_RANGES,
    PLANETARY_DOMICILES,
    NATURAL_RELATIONSHIPS,
    SAPTAVARGA_WEIGHTS,
)


class ShadbalaFactory:
    """
    Factory class for calculating Shadbala for traditional planets.
    """

    # Traditional planets used in Shadbala
    TRADITIONAL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    def __init__(self, subject: AstrologicalSubjectModel):
        self.subject = subject

    def calculate(self) -> ShadbalaModel:
        """
        Calculate full Shadbala for the subject.
        """
        planetary_scores = {}

        for planet_name in self.TRADITIONAL_PLANETS:
            planet_data = self.subject[planet_name.lower()]
            if not planet_data:
                continue

            # Calculate individual components
            sthana = self._calculate_sthana_bala(planet_data)
            dig = self._calculate_dig_bala(planet_data)
            kala = self._calculate_kala_bala(planet_data)
            chesta = self._calculate_chesta_bala(planet_data)
            naisargika = self._calculate_naisargika_bala(planet_name)
            drik = self._calculate_drik_bala(planet_data)

            total_virupas = sthana + dig + kala + chesta + naisargika + drik
            
            planetary_scores[planet_name.lower()] = PlanetaryShadbalaModel(
                sthana_bala=round(sthana, 2),
                dig_bala=round(dig, 2),
                kala_bala=round(kala, 2),
                chesta_bala=round(chesta, 2),
                naisargika_bala=round(naisargika, 2),
                drik_bala=round(drik, 2),
                total_virupas=round(total_virupas, 2),
                total_rupas=round(total_virupas / 60.0, 2),
            )

        return ShadbalaModel(**planetary_scores)

    def _calculate_naisargika_bala(self, planet_name: str) -> float:
        """
        Natural strength is a fixed value based on the planet.
        """
        return NAISARGIKA_BALA_VALUES.get(planet_name, 0.0)

    def _calculate_dig_bala(self, planet: KerykeionPointModel) -> float:
        """
        Directional strength based on proximity to the ideal house cusp.
        Max 60 Virupas, Min 0 Virupas at 180° away.
        """
        max_house_num = DIG_BALA_MAX_POINTS.get(planet.name)
        if not max_house_num:
            return 0.0

        # Map house number to actual cusp name
        house_map = {
            1: "first_house",
            4: "fourth_house",
            7: "seventh_house",
            10: "tenth_house",
        }
        target_cusp_name = house_map[max_house_num]
        target_cusp: KerykeionPointModel = self.subject[target_cusp_name]
        
        # Calculate arc distance
        # Dig Bala = (180 - Arc Distance from Zero Point) / 3
        # Where Zero Point is 180° from Max Point.
        # Simplified: Dig Bala = (60 - (Arc Distance from Max Point / 3))
        
        diff = abs(planet.abs_pos - target_cusp.abs_pos)
        if diff > 180:
            diff = 360 - diff
            
        # Linear degradation: 60 points at 0° distance, 0 points at 180° distance
        # Formula: (180 - diff) / 180 * 60 = (180 - diff) / 3
        dig_bala = (180.0 - diff) / 3.0
        return dig_bala

    def _calculate_chesta_bala(self, planet: KerykeionPointModel) -> float:
        """
        Motional strength based on planetary speed.
        Note: Sun and Moon use a different calculation (Ayana Bala), 
        but in some simplified systems they are assigned based on speed too.
        Standard Parashari: Sun and Moon don't have Chesta Bala (it's 0).
        """
        if planet.name in ["Sun", "Moon"]:
            return 0.0
            
        # Simplified Chesta Bala based on speed relative to average
        # Retrograde planets get high Chesta Bala.
        if planet.retrograde:
            return 60.0 # Standard simplification for retrograde
            
        # For non-retrograde, it depends on speed (slower = stronger)
        # This is a placeholder for a more complex speed-ratio calculation
        return 30.0 

    def _calculate_sthana_bala(self, planet: KerykeionPointModel) -> float:
        """
        Positional strength (Sthana Bala).
        Includes:
        1. Ucha Bala (Exaltation)
        2. Saptavarga Bala (Strength in 7 divisional charts)
        3. Ojhayugmarasiamsa Bala (Odd/Even sign/navamsha)
        4. Kendradi Bala (Strength in houses)
        5. Drekkana Bala (Strength in decanates)
        """
        ucha = self._calculate_ucha_bala(planet)
        saptavarga = self._calculate_saptavarga_bala(planet)
        
        # Simplified: Sum of main components
        return ucha + saptavarga

    def _calculate_ucha_bala(self, planet: KerykeionPointModel) -> float:
        """
        Points based on distance from Debilitation point.
        Max 60 at Exaltation, 0 at Debilitation.
        Formula: Distance from Debilitation / 3
        """
        deb_sign, deb_deg = DEBILITATION_DEGREES.get(planet.name, (0, 0))
        deb_abs = (deb_sign * 30) + deb_deg
        
        diff = abs(planet.abs_pos - deb_abs)
        if diff > 180:
            diff = 360 - diff
            
        # Distance from debilitation: 0° = 0 pts, 180° = 60 pts
        return diff / 3.0

    def _calculate_saptavarga_bala(self, planet: KerykeionPointModel) -> float:
        """
        Calculate strength across 7 divisional charts.
        """
        if not self.subject.vargas:
            return 0.0
            
        total_saptavarga = 0.0
        varga_list = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]
        
        for v_type in varga_list:
            v_chart = self.subject.vargas.get(v_type)
            if not v_chart: continue
            
            p_varga = v_chart.points.get(planet.name.lower())
            if not p_varga: continue
            
            # 1. Check if Moolatrikona (Only in D1)
            if v_type == "D1":
                mt = MOOLATRIKONA_RANGES.get(planet.name)
                if mt and p_varga.sign_num == mt[0] and mt[1] <= p_varga.position <= mt[2]:
                    total_saptavarga += SAPTAVARGA_WEIGHTS["Moolatrikona"]
                    continue
            
            # 2. Check if Own Sign
            if p_varga.sign_num in PLANETARY_DOMICILES.get(planet.name, []):
                total_saptavarga += SAPTAVARGA_WEIGHTS["Own_Sign"]
                continue
                
            # 3. Check Friendship
            # Get the ruler of the sign the planet is in
            ruler = self._get_sign_ruler(p_varga.sign_num)
            if ruler:
                rel = NATURAL_RELATIONSHIPS.get(planet.name, {}).get(ruler, 0)
                if rel == 1: total_saptavarga += SAPTAVARGA_WEIGHTS["Friend"]
                elif rel == -1: total_saptavarga += SAPTAVARGA_WEIGHTS["Enemy"]
                else: total_saptavarga += SAPTAVARGA_WEIGHTS["Neutral"]
                
        return total_saptavarga

    def _get_sign_ruler(self, sign_num: int) -> Optional[str]:
        """
        Returns the name of the traditional ruler of a sign.
        """
        for planet, signs in PLANETARY_DOMICILES.items():
            if sign_num in signs:
                return planet
        return None

    def _calculate_kala_bala(self, planet: KerykeionPointModel) -> float:
        """
        Temporal strength (Kala Bala).
        Includes:
        1. Nathonnatha Bala (Day/Night strength)
        2. Paksha Bala (Moon phase strength)
        """
        nathonnatha = self._calculate_nathonnatha_bala(planet)
        paksha = self._calculate_paksha_bala(planet)
        
        # Total Kala Bala (simplified sum for now)
        return nathonnatha + paksha

    def _calculate_nathonnatha_bala(self, planet: KerykeionPointModel) -> float:
        """
        Points based on Day/Night birth.
        Moon, Mars, Saturn are strong at Night.
        Sun, Jupiter, Venus are strong at Day.
        Mercury is always strong.
        """
        is_diurnal = self.subject.is_diurnal
        
        strong_day = ["Sun", "Jupiter", "Venus"]
        strong_night = ["Moon", "Mars", "Saturn"]
        
        if planet.name == "Mercury":
            return 60.0
        
        if is_diurnal:
            return 60.0 if planet.name in strong_day else 0.0
        else:
            return 60.0 if planet.name in strong_night else 0.0

    def _calculate_paksha_bala(self, planet: KerykeionPointModel) -> float:
        """
        Points based on Moon phase.
        Benefics are strong in Shukla Paksha (Waxing).
        Malefics are strong in Krishna Paksha (Waning).
        Moon's Paksha Bala is (Distance from Sun / 3) capped at 60.
        """
        sun = self.subject.sun
        moon = self.subject.moon
        if not sun or not moon: return 0.0
        
        # Arc distance from Sun to Moon (Waxing)
        dist = moon.abs_pos - sun.abs_pos
        if dist < 0: dist += 360
        
        # 0-180 (Waxing), 180-360 (Waning)
        is_waxing = dist < 180
        
        # Base Paksha Bala for Moon
        # Formula: (dist / 3) for Moon
        moon_paksha = dist / 3.0
        if moon_paksha > 60: moon_paksha = 120 - moon_paksha # Decreases after Full Moon
        
        benefics = ["Jupiter", "Venus", "Moon", "Mercury"]
        malefics = ["Sun", "Mars", "Saturn"]
        
        # Simple mapping: benefics like waxing, malefics like waning
        if planet.name in benefics:
            return moon_paksha
        else:
            return 60.0 - moon_paksha

    def _calculate_chesta_bala(self, planet: KerykeionPointModel) -> float:
        """
        Motional strength based on planetary speed.
        Slower planets (closer to retrograde) are stronger.
        """
        if planet.name in ["Sun", "Moon"]:
            return 0.0
            
        if planet.retrograde:
            return 60.0
            
        # Simplified speed ratio
        # Average speeds in degrees/day
        avg_speeds = {
            "Mars": 0.524,
            "Mercury": 1.383,
            "Jupiter": 0.083,
            "Venus": 1.200,
            "Saturn": 0.033,
        }
        
        avg = avg_speeds.get(planet.name, 1.0)
        speed = abs(planet.speed) if planet.speed is not None else avg
        
        # Ratio of actual speed to average
        ratio = speed / avg
        if ratio > 2.0: ratio = 2.0
        
        # Slower is stronger: 60 at 0 speed, 0 at 2x avg speed
        chesta = (2.0 - ratio) * 30.0
        return max(0.0, min(60.0, chesta))

    def _calculate_drik_bala(self, planet: KerykeionPointModel) -> float:
        """
        Aspectual strength (Drik Bala).
        Continuous arc-based calculation.
        """
        drik_bala = 0.0
        
        benefics = ["Jupiter", "Venus"]
        malefics = ["Sun", "Mars", "Saturn"]
        
        for other_name in self.TRADITIONAL_PLANETS:
            if other_name == planet.name: continue
            
            other = self.subject[other_name.lower()]
            if not other: continue
            
            # Distance from other planet to target planet
            dist = planet.abs_pos - other.abs_pos
            if dist < 0: dist += 360
            
            # Vedic aspects are mostly focused on 180° (Opposition)
            # Full strength at 180°, decreasing to 0 at 30°/300°
            # Simple linear model for all traditional aspects
            
            aspect_strength = 0.0
            if 30 <= dist <= 180:
                aspect_strength = (dist - 30) / 150.0 * 60.0
            elif 180 < dist <= 300:
                aspect_strength = (300 - dist) / 120.0 * 60.0
                
            # Special aspects (Drishti) for Mars, Jupiter, Saturn
            if other_name == "Mars" and (dist == 90 or dist == 210): # 4th and 8th
                 aspect_strength = 60.0
            elif other_name == "Jupiter" and (dist == 120 or dist == 240): # 5th and 9th
                 aspect_strength = 60.0
            elif other_name == "Saturn" and (dist == 60 or dist == 270): # 3rd and 10th
                 aspect_strength = 60.0

            # Weight by nature of aspecting planet
            if other_name in benefics:
                drik_bala += (aspect_strength / 4.0) # Benefic aspect adds 1/4th
            elif other_name in malefics:
                drik_bala -= (aspect_strength / 4.0) # Malefic aspect subtracts 1/4th
                
        return drik_bala
