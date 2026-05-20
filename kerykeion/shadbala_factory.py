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
        Calculate full Shadbala for the subject with exhaustive granular metrics.
        """
        planetary_scores = {}
        base_total_virupas = {}

        for planet_name in self.TRADITIONAL_PLANETS:
            planet_data = self.subject[planet_name.lower()]
            if not planet_data:
                continue

            # 1. Sthana Bala
            sthana_ucha = self._calculate_ucha_bala(planet_data)
            sthana_saptavarga = self._calculate_saptavarga_bala(planet_data)
            sthana_kendradi = self._calculate_kendradi_bala(planet_data)
            sthana_ojhayugma = self._calculate_ojha_bala(planet_data)
            sthana_drekkana = self._calculate_drekkana_bala(planet_data)
            sthana_total = sthana_ucha + sthana_saptavarga + sthana_kendradi + sthana_ojhayugma + sthana_drekkana

            # 2. Dig Bala
            dig_total, dig_dist = self._calculate_dig_bala(planet_data)

            # 3. Kala Bala
            kala_nathonnatha = self._calculate_nathonnatha_bala(planet_data)
            kala_paksha = self._calculate_paksha_bala(planet_data)
            
            # Time Lords sub-breakdown
            v_lord, m_lord = self._get_varsha_maasa_lords()
            kala_varsha = 15.0 if planet_data.name == v_lord else 0.0
            kala_maasa = 30.0 if planet_data.name == m_lord else 0.0
            kala_dina = 45.0 if planet_data.name == self.subject.panchang.vara else 0.0
            kala_hora = 60.0 if planet_data.name == self._get_hora_lord() else 0.0
            
            kala_ayana = self._calculate_ayana_bala(planet_data)
            kala_total = kala_nathonnatha + kala_paksha + kala_varsha + kala_maasa + kala_dina + kala_hora + kala_ayana

            # 4. Chesta Bala
            chesta_total, chesta_ratio = self._calculate_chesta_bala_with_ratio(planet_data)

            # 5. Naisargika Bala
            naisargika_total = self._calculate_naisargika_bala(planet_name)

            # 6. Drik Bala
            drik_total, drik_ben, drik_mal = self._calculate_drik_bala_with_sums(planet_data)

            total_virupas = sthana_total + dig_total + kala_total + chesta_total + naisargika_total + drik_total
            base_total_virupas[planet_name] = total_virupas

            planetary_scores[planet_name.lower()] = {
                "sthana_bala": round(sthana_total, 2),
                "sthana_ucha": round(sthana_ucha, 2),
                "sthana_saptavarga": round(sthana_saptavarga, 2),
                "sthana_kendradi": round(sthana_kendradi, 2),
                "sthana_ojhayugma": round(sthana_ojhayugma, 2),
                "sthana_drekkana": round(sthana_drekkana, 2),
                "dig_bala": round(dig_total, 2),
                "dig_distance": round(dig_dist, 2),
                "kala_bala": round(kala_total, 2),
                "kala_nathonnatha": round(kala_nathonnatha, 2),
                "kala_paksha": round(kala_paksha, 2),
                "kala_varsha": round(kala_varsha, 2),
                "kala_maasa": round(kala_maasa, 2),
                "kala_dina": round(kala_dina, 2),
                "kala_hora": round(kala_hora, 2),
                "kala_ayana": round(kala_ayana, 2),
                "chesta_bala": round(chesta_total, 2),
                "chesta_ratio": round(chesta_ratio, 2),
                "naisargika_bala": round(naisargika_total, 2),
                "drik_bala": round(drik_total, 2),
                "drik_benefic": round(drik_ben, 2),
                "drik_malefic": round(drik_mal, 2),
            }

        # --- 7. Yudha Bala (Planetary War) ---
        yudha_adjustments = self._calculate_yudha_bala(base_total_virupas)
        
        final_models = {}
        for p_name, base_scores in planetary_scores.items():
            cap_name = p_name.capitalize()
            yudha_v = yudha_adjustments.get(cap_name, 0.0)
            total_v = base_total_virupas[cap_name] + yudha_v
            total_r = total_v / 60.0
            
            min_req = SHADBALA_MINIMUM_REQUIREMENTS.get(cap_name, 5.0)
            is_strong = total_r >= min_req
            
            final_models[p_name] = PlanetaryShadbalaModel(
                **base_scores,
                yudha_bala=round(yudha_v, 2),
                total_virupas=round(total_v, 2),
                total_rupas=round(total_r, 2),
                minimum_required=min_req,
                is_strong=is_strong,
            )

        return ShadbalaModel(**final_models)

    def _calculate_chesta_bala_with_ratio(self, planet: KerykeionPointModel) -> Tuple[float, float]:
        """
        Returns (Bala, Ratio).
        """
        if planet.name in ["Sun", "Moon"]: return 0.0, 1.0
        if planet.retrograde: return 60.0, 0.0
            
        avg_speeds = {"Mars": 0.524, "Mercury": 1.383, "Jupiter": 0.083, "Venus": 1.200, "Saturn": 0.033}
        avg = avg_speeds.get(planet.name, 1.0)
        speed = abs(planet.speed) if planet.speed is not None else avg
        
        ratio = speed / avg
        if ratio > 2.0: ratio = 2.0
        bala = max(0.0, min(60.0, (2.0 - ratio) * 30.0))
        return bala, ratio

    def _calculate_drik_bala_with_sums(self, planet: KerykeionPointModel) -> Tuple[float, float, float]:
        """
        Returns (Net, Benefic Sum, Malefic Sum).
        """
        benefic_sum = 0.0
        malefic_sum = 0.0

        for other_name in self.TRADITIONAL_PLANETS:
            if other_name == planet.name:
                continue

            other = self.subject[other_name.lower()]
            if not other:
                continue

            dist = planet.abs_pos - other.abs_pos
            if dist < 0: dist += 360

            aspect_strength = 0.0
            if 30 <= dist <= 180:
                aspect_strength = (dist - 30) / 150.0 * 60.0
            elif 180 < dist <= 300:
                aspect_strength = (300 - dist) / 120.0 * 60.0

            special_strength = 0.0
            if other_name == "Mars":
                if abs(dist - 90) <= 15: special_strength = 60.0 * (1 - abs(dist - 90) / 15)
                elif abs(dist - 210) <= 15: special_strength = 60.0 * (1 - abs(dist - 210) / 15)
            elif other_name == "Jupiter":
                if abs(dist - 120) <= 15: special_strength = 60.0 * (1 - abs(dist - 120) / 15)
                elif abs(dist - 240) <= 15: special_strength = 60.0 * (1 - abs(dist - 240) / 15)
            elif other_name == "Saturn":
                if abs(dist - 60) <= 15: special_strength = 60.0 * (1 - abs(dist - 60) / 15)
                elif abs(dist - 270) <= 15: special_strength = 60.0 * (1 - abs(dist - 270) / 15)

            aspect_strength = max(aspect_strength, special_strength)

            if self._is_benefic(other_name):
                benefic_sum += aspect_strength / 4.0
            else:
                malefic_sum += aspect_strength / 4.0

        return benefic_sum - malefic_sum, benefic_sum, malefic_sum

    def _calculate_yudha_bala(self, base_strengths: Dict[str, float]) -> Dict[str, float]:
        """
        Planetary War (Yudha Bala).
        Only for Mars, Mercury, Jupiter, Venus, and Saturn.
        Conjunction within 1 degree.
        """
        true_planets = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        adjustments = {p: 0.0 for p in self.TRADITIONAL_PLANETS}
        
        # Fixed classical diameters for Yudha calculation (Raman's standard)
        diameters = {
            "Mars": 9.4, "Mercury": 6.6, "Jupiter": 190.4, "Venus": 16.6, "Saturn": 157.8
        }
        
        checked_pairs = set()
        
        for p1_name in true_planets:
            p1 = self.subject[p1_name.lower()]
            if not p1: continue
            
            for p2_name in true_planets:
                if p1_name == p2_name: continue
                pair = tuple(sorted((p1_name, p2_name)))
                if pair in checked_pairs: continue
                checked_pairs.add(pair)
                
                p2 = self.subject[p2_name.lower()]
                if not p2: continue
                
                # Check for conjunction within 1 degree
                dist = abs(p1.abs_pos - p2.abs_pos)
                if dist > 180: dist = 360 - dist
                
                if dist <= 1.0:
                    # War detected!
                    s1, s2 = base_strengths[p1_name], base_strengths[p2_name]
                    d1, d2 = diameters[p1_name], diameters[p2_name]
                    
                    diff_s = abs(s1 - s2)
                    diff_d = abs(d1 - d2)
                    
                    # Transfer amount
                    transfer = diff_s / (diff_d if diff_d != 0 else 1.0)
                    
                    # Determine victor
                    if d1 > d2:
                        adjustments[p1_name] += transfer
                        adjustments[p2_name] -= transfer
                    else:
                        adjustments[p2_name] += transfer
                        adjustments[p1_name] -= transfer
                        
        return adjustments

    # --- 1. Sthana Bala (Positional Strength) ---

    def _calculate_sthana_bala(self, planet: KerykeionPointModel) -> float:
        """
        Positional strength (Sthana Bala).
        """
        ucha = self._calculate_ucha_bala(planet)
        saptavarga = self._calculate_saptavarga_bala(planet)
        kendradi = self._calculate_kendradi_bala(planet)
        ojha = self._calculate_ojha_bala(planet)
        drekkana = self._calculate_drekkana_bala(planet)
        
        return ucha + saptavarga + kendradi + ojha + drekkana

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
                # Check for Exaltation
                ex_sign, ex_deg = EXALTATION_DEGREES.get(planet.name, (0, 0))
                if p_varga.sign_num == ex_sign and abs(p_varga.position - ex_deg) < 1.0:
                    total_saptavarga += SAPTAVARGA_WEIGHTS["Exaltation"]
                    continue
                
                # Check for Debilitation
                deb_sign, deb_deg = DEBILITATION_DEGREES.get(planet.name, (0, 0))
                if p_varga.sign_num == deb_sign and abs(p_varga.position - deb_deg) < 1.0:
                    total_saptavarga += SAPTAVARGA_WEIGHTS["Debilitation"]
                    continue

                # Check for Moolatrikona
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
        h_num = self._get_house_num(planet.house)
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

    def _calculate_drekkana_bala(self, planet: KerykeionPointModel) -> float:
        """
        Drekkana Bala (Positional strength based on decan and gender).
        Male planets (Sun, Mars, Jupiter) in 1st Drekkana (0-10) = 15
        Hermaphrodite (Mercury, Saturn) in 2nd Drekkana (10-20) = 15
        Female (Moon, Venus) in 3rd Drekkana (20-30) = 15
        """
        male_planets = ["Sun", "Mars", "Jupiter"]
        female_planets = ["Moon", "Venus"]
        hermaphrodite_planets = ["Mercury", "Saturn"]
        
        decan = int(planet.position // 10)
        
        if decan == 0 and planet.name in male_planets: return 15.0
        if decan == 1 and planet.name in hermaphrodite_planets: return 15.0
        if decan == 2 and planet.name in female_planets: return 15.0
        
        return 0.0

    # --- 2. Dig Bala (Directional Strength) ---

    def _calculate_dig_bala(self, planet: KerykeionPointModel) -> Tuple[float, float]:
        """
        Directional strength based on proximity to the ideal house cusp.
        Returns (Total Dig Bala, Distance from Peak).
        """
        max_house_num = DIG_BALA_MAX_POINTS.get(planet.name)
        if not max_house_num: return 0.0, 0.0

        house_map = {1: "first_house", 4: "fourth_house", 7: "seventh_house", 10: "tenth_house"}
        target_cusp: KerykeionPointModel = self.subject[house_map[max_house_num]]
        
        diff = abs(planet.abs_pos - target_cusp.abs_pos)
        if diff > 180: diff = 360 - diff
        
        bala = (180.0 - diff) / 3.0
        return max(0.0, bala), diff

    # --- 3. Kala Bala (Temporal Strength) ---

    def _calculate_kala_bala(self, planet: KerykeionPointModel) -> float:
        """
        Temporal strength (Kala Bala).
        Composed of: Nathonnatha, Paksha, Tribhaga, Varsha, Maasa, Dina, Hora, and Ayana Bala.
        """
        # 1. Nathonnatha Bala (Day/Night strength)
        nathonnatha = self._calculate_nathonnatha_bala(planet)
        
        # 2. Paksha Bala (Moon phase strength)
        paksha = self._calculate_paksha_bala(planet)
        
        # 3. Time Lords (Dina, Hora, Varsha, Maasa)
        time_lords_bala = self._calculate_time_lords_bala(planet)
        
        # 4. Ayana Bala (Equinoctial strength)
        ayana = self._calculate_ayana_bala(planet)
        
        return nathonnatha + paksha + time_lords_bala + ayana

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

    def _calculate_time_lords_bala(self, planet: KerykeionPointModel) -> float:
        """
        Combined strength from Varsha, Maasa, Dina, and Hora lords.
        """
        total = 0.0
        
        # 1. Dina Bala (Day Lord) - 45 Virupas
        if planet.name == self.subject.panchang.vara:
            total += 45.0
            
        # 2. Hora Bala (Hour Lord) - 60 Virupas
        hora_lord = self._get_hora_lord()
        if planet.name == hora_lord:
            total += 60.0
            
        # 3. Varsha (Year) and Maasa (Month) Lords
        v_lord, m_lord = self._get_varsha_maasa_lords()
        if planet.name == v_lord: total += 15.0
        if planet.name == m_lord: total += 30.0
            
        return total

    def _get_hora_lord(self) -> str:
        """
        Calculates the lord of the planetary hour.
        """
        from kerykeion.panchang_utils import get_sunrise_sunset
        
        jd = self.subject.julian_day
        lat, lng = self.subject.lat, self.subject.lng
        
        # Get sunrise for the current day
        sr, _ = get_sunrise_sunset(jd, lat, lng)
        
        # If born before sunrise, use previous day's sunrise
        if jd < sr:
            sr, _ = get_sunrise_sunset(jd - 1.0, lat, lng)
            
        # 1 planetary hour = 1/24th of a day (approx 1 hour)
        # Parashari sequence: Sun, Venus, Mercury, Moon, Saturn, Jupiter, Mars
        sequence = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
        
        # Find start lord (Day Lord)
        day_lord = self.subject.panchang.vara
        start_idx = sequence.index(day_lord) if day_lord in sequence else 0
        
        hours_since_sunrise = (jd - sr) * 24.0
        hora_idx = (start_idx + int(hours_since_sunrise)) % 7
        
        return sequence[hora_idx]

    def _get_varsha_maasa_lords(self) -> Tuple[str, str]:
        """
        Calculates Varsha and Maasa lords using Ahargana approximation.
        Epoch: Jan 1, 1900 (JD 2415020.5)
        """
        # Days elapsed since epoch
        ahargana = self.subject.julian_day - 2415020.5
        
        # Varsha Lord (Every 360 days, jumps 3 weekdays)
        v_idx = (int(ahargana // 360) * 3) % 7
        
        # Maasa Lord (Every 30 days, jumps 2 weekdays)
        m_idx = (int(ahargana // 30) * 2) % 7
        
        # Weekday mapping (0=Sun, 1=Moon, ..., 6=Sat)
        days = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        
        # Jan 1, 1900 was a Monday (index 1)
        v_lord = days[(1 + v_idx) % 7]
        m_lord = days[(1 + m_idx) % 7]
        
        return v_lord, m_lord

    def _calculate_ayana_bala(self, planet: KerykeionPointModel) -> float:
        """
        Ayana Bala (Equinoctial strength based on declination).
        (24 + Declination) * 1.25 for North-strong planets.
        """
        # North-strong: Sun, Mars, Jupiter, Venus
        # South-strong: Moon, Saturn
        # Both: Mercury
        
        declination = planet.declination if planet.declination is not None else 0.0
        
        # Adjust declination sign based on planet's preference
        if planet.name in ["Moon", "Saturn"]:
            effective_dec = -declination
        elif planet.name == "Mercury":
            effective_dec = abs(declination)
        else:
            effective_dec = declination
            
        # Raman's formula approximation: (24 + eff_dec) * 1.25
        # This yields 30 at 0 dec, 60 at 24 North, 0 at 24 South (for North-strong)
        bala = (24.0 + effective_dec) * 1.25
        
        if planet.name == "Sun":
            bala *= 2.0 # Sun's Ayana Bala is doubled
            
        return max(0.0, bala)

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
        Sum of (Benefic Aspect Strengths / 4) - Sum of (Malefic Aspect Strengths / 4).
        """
        drik_bala = 0.0

        for other_name in self.TRADITIONAL_PLANETS:
            if other_name == planet.name:
                continue

            other = self.subject[other_name.lower()]
            if not other:
                continue

            # Calculate distance from 'other' to 'planet' (forward)
            dist = planet.abs_pos - other.abs_pos
            if dist < 0:
                dist += 360

            # 1. Base Aspect Strength (Degree-based)
            # 0 at 30, 60 at 180, 0 at 300
            aspect_strength = 0.0
            if 30 <= dist <= 180:
                aspect_strength = (dist - 30) / 150.0 * 60.0
            elif 180 < dist <= 300:
                aspect_strength = (300 - dist) / 120.0 * 60.0

            # 2. Special Aspects (Mars, Jupiter, Saturn)
            # We use a 15-degree window around the target degree to graduate the strength.
            special_strength = 0.0
            if other_name == "Mars":
                # Full aspect on 4th (90) and 8th (210) houses
                if abs(dist - 90) <= 15:
                    special_strength = 60.0 * (1 - abs(dist - 90) / 15)
                elif abs(dist - 210) <= 15:
                    special_strength = 60.0 * (1 - abs(dist - 210) / 15)
            elif other_name == "Jupiter":
                # Full aspect on 5th (120) and 9th (240) houses
                if abs(dist - 120) <= 15:
                    special_strength = 60.0 * (1 - abs(dist - 120) / 15)
                elif abs(dist - 240) <= 15:
                    special_strength = 60.0 * (1 - abs(dist - 240) / 15)
            elif other_name == "Saturn":
                # Full aspect on 3rd (60) and 10th (270) houses
                if abs(dist - 60) <= 15:
                    special_strength = 60.0 * (1 - abs(dist - 60) / 15)
                elif abs(dist - 270) <= 15:
                    special_strength = 60.0 * (1 - abs(dist - 270) / 15)

            aspect_strength = max(aspect_strength, special_strength)

            # 3. Apply Benefic/Malefic Factor
            if self._is_benefic(other_name):
                drik_bala += aspect_strength / 4.0
            else:
                drik_bala -= aspect_strength / 4.0

        return drik_bala

    # --- Utils ---

    def _is_benefic(self, planet_name: str) -> bool:
        """
        Determines if a planet is a benefic or malefic for Drik Bala.
        """
        if planet_name in ["Jupiter", "Venus"]:
            return True
        if planet_name in ["Sun", "Mars", "Saturn"]:
            return False

        if planet_name == "Moon":
            # Moon is benefic if waxing (Shukla Paksha).
            sun, moon = self.subject.sun, self.subject.moon
            if not sun or not moon:
                return True
            dist = moon.abs_pos - sun.abs_pos
            if dist < 0:
                dist += 360
            return 0 < dist < 180

        if planet_name == "Mercury":
            # Mercury is benefic unless associated with malefics in the same sign.
            mercury = self.subject.mercury
            if not mercury:
                return True
            for malefic in ["Sun", "Mars", "Saturn"]:
                m_data = self.subject[malefic.lower()]
                if m_data and m_data.sign_num == mercury.sign_num:
                    return False
            return True

        return True

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
