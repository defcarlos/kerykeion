# -*- coding: utf-8 -*-
"""
Vimsottari Dasha Factory
========================

This module provides the factory for calculating the Vimsottari Dasha system,
a 120-year planetary cycle system used in Vedic astrology for predictive timing.

The system is based on the position of the Moon at birth in its Nakshatra.

This is part of Kerykeion (C) 2025 Giacomo Battaglia
"""

from typing import List, Tuple
from datetime import datetime, timezone
import swisseph as swe

from kerykeion.schemas.kr_models import (
    VimsottariDashaModel,
    MahadashaModel,
    AntardashaModel,
    PratyantardashaModel,
    AstrologicalSubjectModel,
)
from kerykeion.schemas.kr_literals import NakshatraLord


class VimsottariDashaFactory:
    """
    Factory class to calculate the Vimsottari Dasha periods for an astrological subject.
    """

    # Vimsottari sequence and durations (in years)
    DASHA_LORDS: Tuple[NakshatraLord, ...] = (
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
    DASHA_DURATIONS: Tuple[int, ...] = (7, 20, 6, 10, 7, 18, 16, 19, 17)
    
    # Standard Gregorian year in days for dasha calculation
    DAYS_PER_YEAR = 365.2425
    TOTAL_CYCLE_YEARS = 120

    def __init__(self, subject: AstrologicalSubjectModel):
        self.subject = subject
        if not self.subject.moon:
            raise ValueError("Vimsottari Dasha requires Moon position data.")

    def _jd_to_datetime(self, jd: float) -> datetime:
        """Helper to convert Julian Day to UTC datetime."""
        y, m, d, h = swe.revjul(jd)
        hours = int(h)
        minutes = int((h - hours) * 60)
        seconds = int(((h - hours) * 60 - minutes) * 60)
        micro = int((((h - hours) * 60 - minutes) * 60 - seconds) * 1000000)
        # Avoid microsecond overflow/underflow if any
        micro = min(max(0, micro), 999999)
        return datetime(y, m, d, hours, minutes, seconds, micro, tzinfo=timezone.utc)

    def calculate(self) -> VimsottariDashaModel:
        """
        Calculate the complete Vimsottari Dasha cycles.
        """
        # 1. Determine sidereal Moon position for Nakshatra calculation
        # We use the nakshatra_ayanamsa_value if available, otherwise 0 (already sidereal)
        ayanamsa = self.subject.get("nakshatra_ayanamsa_value") or 0.0
        moon_abs_pos = self.subject.moon.abs_pos
        sidereal_moon = (moon_abs_pos - ayanamsa) % 360.0

        # 2. Identify the starting Nakshatra and the fraction passed
        # Each Nakshatra is 13°20' (13.33333333 degrees)
        nak_width = 360.0 / 27.0
        nak_index = int(sidereal_moon / nak_width)
        fraction_passed = (sidereal_moon % nak_width) / nak_width

        # 3. Find the starting Mahadasha lord
        # Dasha lords cycle every 9 Nakshatras
        start_lord_idx = nak_index % 9
        
        # 4. Calculate the technical start of the first Mahadasha (before birth)
        start_lord_duration_years = self.DASHA_DURATIONS[start_lord_idx]
        days_already_passed = fraction_passed * start_lord_duration_years * self.DAYS_PER_YEAR
        
        current_jd = self.subject.julian_day - days_already_passed
        
        mahadashas: List[MahadashaModel] = []
        
        # 5. Generate the 120-year cycle starting from the birth lord
        # We calculate at least one full 120-year cycle
        for i in range(9):
            lord_idx = (start_lord_idx + i) % 9
            lord_name = self.DASHA_LORDS[lord_idx]
            m_years = self.DASHA_DURATIONS[lord_idx]
            m_duration_days = m_years * self.DAYS_PER_YEAR
            
            m_start_jd = current_jd
            m_end_jd = m_start_jd + m_duration_days
            
            antardashas: List[AntardashaModel] = []
            a_current_jd = m_start_jd
            
            # Sub-periods (Antardashas)
            for j in range(9):
                a_lord_idx = (lord_idx + j) % 9
                a_lord_name = self.DASHA_LORDS[a_lord_idx]
                a_years = self.DASHA_DURATIONS[a_lord_idx]
                
                # Antardasha duration = (Mahadasha Years * Antardasha Years) / 120
                a_duration_years = (m_years * a_years) / self.TOTAL_CYCLE_YEARS
                a_duration_days = a_duration_years * self.DAYS_PER_YEAR
                
                a_start_jd = a_current_jd
                a_end_jd = a_start_jd + a_duration_days
                
                pratyantardashas: List[PratyantardashaModel] = []
                p_current_jd = a_start_jd
                
                # Sub-sub-periods (Pratyantardashas)
                for k in range(9):
                    p_lord_idx = (a_lord_idx + k) % 9
                    p_lord_name = self.DASHA_LORDS[p_lord_idx]
                    p_years = self.DASHA_DURATIONS[p_lord_idx]
                    
                    # Pratyantardasha duration = (Antardasha Days * Lord Years) / 120
                    p_duration_days = (a_duration_days * p_years) / self.TOTAL_CYCLE_YEARS
                    
                    p_start_jd = p_current_jd
                    p_end_jd = p_start_jd + p_duration_days
                    
                    pratyantardashas.append(PratyantardashaModel(
                        lord=p_lord_name,
                        level="Pratyantardasha",
                        start_date=self._jd_to_datetime(p_start_jd),
                        end_date=self._jd_to_datetime(p_end_jd),
                        duration_days=p_duration_days
                    ))
                    
                    p_current_jd = p_end_jd
                
                antardashas.append(AntardashaModel(
                    lord=a_lord_name,
                    level="Antardasha",
                    start_date=self._jd_to_datetime(a_start_jd),
                    end_date=self._jd_to_datetime(a_end_jd),
                    duration_days=a_duration_days,
                    pratyantardashas=pratyantardashas
                ))
                
                a_current_jd = a_end_jd
                
            mahadashas.append(MahadashaModel(
                lord=lord_name,
                level="Mahadasha",
                start_date=self._jd_to_datetime(m_start_jd),
                end_date=self._jd_to_datetime(m_end_jd),
                duration_days=m_duration_days,
                antardashas=antardashas
            ))
            
            current_jd = m_end_jd
            
        return VimsottariDashaModel(mahadashas=mahadashas)
