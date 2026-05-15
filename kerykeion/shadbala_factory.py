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
    SHADBALA_MINIMUM_REQUIREMENTS,
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
            total_rupas = total_virupas / 60.0
            
            min_req = SHADBALA_MINIMUM_REQUIREMENTS.get(planet_name, 5.0)
            is_strong = total_rupas >= min_req

            planetary_scores[planet_name.lower()] = PlanetaryShadbalaModel(
                sthana_bala=round(sthana, 2),
                dig_bala=round(dig, 2),
                kala_bala=round(kala, 2),
                chesta_bala=round(chesta, 2),
                naisargika_bala=round(naisargika, 2),
                drik_bala=round(drik, 2),
                total_virupas=round(total_virupas, 2),
                total_rupas=round(total_rupas, 2),
                minimum_required=min_req,
                is_strong=is_strong,
            )

        return ShadbalaModel(**planetary_scores)

    # --- 1. Sthana Bala (Positional Strength) ---

    def _calculate_sthana_bala(self, planet: KerykeionPointModel) -> float:
        """
        Positional strength (Sthana Bala).
        """
        ucha = self._calculate_ucha_bala(planet)
        saptavarga = self._calculate_saptavarga_bala(planet)
        kendradi = self._calculate_kendradi_bala(planet)
        ojha = self._calculate_ojha_bala(planet)
        
        return ucha + saptavarga + kendradi + ojha

    def _calculate_ucha_bala(self, planet: KerykeionPointModel) -> float:
        """
        Points based on distance from Debilitation point.
        Max 60 at Exaltation, 0 at Debilitation.
        """
        deb_sign, deb_deg = DEBILITATION_DEGREES.get(planet.name, (0, 0))
        deb_abs = (deb_sign * 30) + deb_deg
        
        diff = abs(planet.abs_pos - deb_abs)
        if diff > 180:
            diff = 360 - diff
            
        return diff / 3.0

    def _calculate_saptavarga_bala(self, planet: KerykeionPointModel) -> float:
        """
        Calculate strength across 7 divisional charts.
        Includes combined friendship (Natural + Temporary).
        """
        if not self.subject.vargas:
            return 0.0
            
        total_saptavarga = 0.0
        varga_list = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]
        
        temp_friends = self._get_temporary_friends(planet.name)
        
        for v_type in varga_list:
            v_chart = self.subject.vargas.get(v_type)
            if not v_chart: continue
            
            p_varga = v_chart.points.get(planet.name.lower())
            if not p_varga: continue
            
            if v_type == "D1":
                mt = MOOLATRIKONA_RANGES.get(planet.name)
                if mt and p_varga.sign_num == mt[0] and mt[1] <= p_varga.position <= mt[2]:
                    total_saptavarga += SAPTAVARGA_WEIGHTS["Moolatrikona"]
                    continue
            
            if p_varga.sign_num in PLANETARY_DOMICILES.get(planet.name, []):
                total_saptavarga += SAPTAVARGA_WEIGHTS["Own_Sign"]
                continue
                
            ruler = self._get_sign_ruler(p_varga.sign_num)
            if ruler:
                natural_rel = NATURAL_RELATIONSHIPS.get(planet.name, {}).get(ruler, 0)
                temp_rel = 1 if ruler in temp_friends else -1
                combined = natural_rel + temp_rel
                
                if combined >= 2: total_saptavarga += SAPTAVARGA_WEIGHTS["Great_Friend"]
                elif combined == 1: total_saptavarga += SAPTAVARGA_WEIGHTS["Friend"]
                elif combined == -1: total_saptavarga += SAPTAVARGA_WEIGHTS["Enemy"]
                elif combined <= -2: total_saptavarga += SAPTAVARGA_WEIGHTS["Great_Enemy"]
                else: total_saptavarga += SAPTAVARGA_WEIGHTS["Neutral"]
                
        return total_saptavarga

    def _calculate_kendradi_bala(self, planet: KerykeionPointModel) -> float:
        """
        Strength based on house type.
        Angular (1,4,7,10) = 60, Succedent (2,5,8,11) = 30, Cadent = 15
        """
        if not planet.house: return 0.0
        h_num = int(planet.house.split("_")[0])
        if h_num in [1, 4, 7, 10]: return 60.0
        if h_num in [2, 5, 8, 11]: return 30.0
        return 15.0

    def _calculate_ojha_bala(self, planet: KerykeionPointModel) -> float:
        """
        Ojhayugmarasiamsa Bala (Odd/Even sign parity).
        15 points each for matching parity in D1 and D9.
        """
        total_ojha = 0.0
        odd_planets = ["Sun", "Mars", "Jupiter", "Mercury", "Saturn"]
        even_planets = ["Moon", "Venus"]
        
        is_odd_sign = planet.sign_num % 2 == 0 # 0=Ari (Odd), 1=Tau (Even)
        if planet.name in odd_planets and is_odd_sign: total_ojha += 15.0
        elif planet.name in even_planets and not is_odd_sign: total_ojha += 15.0
        
        d9 = self.subject.vargas.get("D9") if self.subject.vargas else None
        if d9:
            p_d9 = d9.points.get(planet.name.lower())
            if p_d9:
                is_odd_d9 = p_d9.sign_num % 2 == 0
                if planet.name in odd_planets and is_odd_d9: total_ojha += 15.0
                elif planet.name in even_planets and not is_odd_d9: total_ojha += 15.0
                
        return total_ojha

    # --- 2. Dig Bala (Directional Strength) ---

    def _calculate_dig_bala(self, planet: KerykeionPointModel) -> float:
        """
        Directional strength based on proximity to the ideal house cusp.
        """
        max_house_num = DIG_BALA_MAX_POINTS.get(planet.name)
        if not max_house_num: return 0.0

        house_map = {1: "first_house", 4: "fourth_house", 7: "seventh_house", 10: "tenth_house"}
        target_cusp: KerykeionPointModel = self.subject[house_map[max_house_num]]
        
        diff = abs(planet.abs_pos - target_cusp.abs_pos)
        if diff > 180: diff = 360 - diff
        return (180.0 - diff) / 3.0

    # --- 3. Kala Bala (Temporal Strength) ---

    def _calculate_kala_bala(self, planet: KerykeionPointModel) -> float:
        """
        Temporal strength (Kala Bala).
        """
        nathonnatha = self._calculate_nathonnatha_bala(planet)
        paksha = self._calculate_paksha_bala(planet)
        return nathonnatha + paksha

    def _calculate_nathonnatha_bala(self, planet: KerykeionPointModel) -> float:
        """
        Points based on Day/Night birth.
        """
        is_diurnal = self.subject.is_diurnal
        strong_day = ["Sun", "Jupiter", "Venus"]
        strong_night = ["Moon", "Mars", "Saturn"]
        
        if planet.name == "Mercury": return 60.0
        if is_diurnal: return 60.0 if planet.name in strong_day else 0.0
        return 60.0 if planet.name in strong_night else 0.0

    def _calculate_paksha_bala(self, planet: KerykeionPointModel) -> float:
        """
        Points based on Moon phase.
        """
        sun, moon = self.subject.sun, self.subject.moon
        if not sun or not moon: return 0.0
        
        dist = moon.abs_pos - sun.abs_pos
        if dist < 0: dist += 360
        
        moon_paksha = dist / 3.0
        if moon_paksha > 60: moon_paksha = 120 - moon_paksha
        
        if planet.name in ["Jupiter", "Venus", "Moon", "Mercury"]: return moon_paksha
        return 60.0 - moon_paksha

    # --- 4. Chesta Bala (Motional Strength) ---

    def _calculate_chesta_bala(self, planet: KerykeionPointModel) -> float:
        """
        Motional strength based on planetary speed.
        """
        if planet.name in ["Sun", "Moon"]: return 0.0
        if planet.retrograde: return 60.0
            
        avg_speeds = {"Mars": 0.524, "Mercury": 1.383, "Jupiter": 0.083, "Venus": 1.200, "Saturn": 0.033}
        avg = avg_speeds.get(planet.name, 1.0)
        speed = abs(planet.speed) if planet.speed is not None else avg
        
        ratio = speed / avg
        if ratio > 2.0: ratio = 2.0
        return max(0.0, min(60.0, (2.0 - ratio) * 30.0))

    # --- 5. Naisargika Bala (Natural Strength) ---

    def _calculate_naisargika_bala(self, planet_name: str) -> float:
        """
        Natural strength is a fixed value based on the planet.
        """
        return NAISARGIKA_BALA_VALUES.get(planet_name, 0.0)

    # --- 6. Drik Bala (Aspectual Strength) ---

    def _calculate_drik_bala(self, planet: KerykeionPointModel) -> float:
        """
        Aspectual strength (Drik Bala).
        """
        drik_bala = 0.0
        benefics, malefics = ["Jupiter", "Venus"], ["Sun", "Mars", "Saturn"]
        
        for other_name in self.TRADITIONAL_PLANETS:
            if other_name == planet.name: continue
            other = self.subject[other_name.lower()]
            if not other: continue
            
            dist = planet.abs_pos - other.abs_pos
            if dist < 0: dist += 360
            
            aspect_strength = 0.0
            if 30 <= dist <= 180: aspect_strength = (dist - 30) / 150.0 * 60.0
            elif 180 < dist <= 300: aspect_strength = (300 - dist) / 120.0 * 60.0
                
            if other_name == "Mars" and (dist == 90 or dist == 210): aspect_strength = 60.0
            elif other_name == "Jupiter" and (dist == 120 or dist == 240): aspect_strength = 60.0
            elif other_name == "Saturn" and (dist == 60 or dist == 270): aspect_strength = 60.0

            if other_name in benefics: drik_bala += (aspect_strength / 4.0)
            elif other_name in malefics: drik_bala -= (aspect_strength / 4.0)
                
        return drik_bala

    # --- Utils ---

    def _get_temporary_friends(self, planet_name: str) -> List[str]:
        """
        Vedic Temporary Friendship (Tatkalika Maitri).
        """
        friends = []
        target = self.subject[planet_name.lower()]
        if not target: return []
        
        target_h = self._get_house_num(target.house)
        if target_h == 0: return []

        for other_name in self.TRADITIONAL_PLANETS:
            if other_name == planet_name: continue
            other = self.subject[other_name.lower()]
            if not other: continue
            
            other_h = self._get_house_num(other.house)
            if other_h == 0: continue
            
            dist = (other_h - target_h) % 12
            if dist == 0: dist = 12
            if dist in [2, 3, 4, 10, 11, 12]: friends.append(other_name)
        return friends

    def _get_house_num(self, house_name: Optional[str]) -> int:
        """
        Converts house string (e.g., 'First_House') to integer (1-12).
        """
        if not house_name: return 0
        
        mapping = {
            "First_House": 1, "Second_House": 2, "Third_House": 3, "Fourth_House": 4,
            "Fifth_House": 5, "Sixth_House": 6, "Seventh_House": 7, "Eighth_House": 8,
            "Ninth_House": 9, "Tenth_House": 10, "Eleventh_House": 11, "Twelfth_House": 12
        }
        return mapping.get(house_name, 0)

    def _get_sign_ruler(self, sign_num: int) -> Optional[str]:
        """
        Returns the name of the traditional ruler of a sign.
        """
        for planet, signs in PLANETARY_DOMICILES.items():
            if sign_num in signs: return planet
        return None
