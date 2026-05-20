# -*- coding: utf-8 -*-
"""
Vedic Aspect (Graha Drishti) Utilities
======================================

This module provides utility functions for calculating sign-based Vedic 
aspects (Drishti). Unlike Western aspects, Drishti is based on the 
planetary "glance" from sign to sign, not on degree-based orbs.

This is part of Kerykeion (C) 2025 Giacomo Battaglia
"""

from typing import List, Union
from kerykeion.schemas.kr_models import (
    AstrologicalSubjectModel, 
    CompositeSubjectModel, 
    PlanetReturnModel, 
    VedicAspectModel
)

def get_graha_drishti(
    subject: Union[AstrologicalSubjectModel, CompositeSubjectModel, PlanetReturnModel]
) -> List[VedicAspectModel]:
    """
    Calculate all sign-based Vedic aspects (Graha Drishti) for a subject.
    
    Rules:
    - All planets aspect the 7th house/sign from their position.
    - Mars has special aspects on the 4th and 8th signs.
    - Jupiter has special aspects on the 5th and 9th signs.
    - Saturn has special aspects on the 3rd and 10th signs.
    
    Counting is inclusive: Sign the planet is in is 1.
    """
    aspects = []
    traditional_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Mean_North_Lunar_Node", "True_North_Lunar_Node"]
    
    active_planets = [p for p in traditional_planets if subject[p.lower()] is not None]
    
    for p1_name in active_planets:
        p1 = subject[p1_name.lower()]
        p1_sign_num = p1.sign_num
        
        # 1. Standard 7th Aspect (All planets including Nodes)
        target_7th = (p1_sign_num + 6) % 12
        aspects.extend(_find_planets_in_sign(subject, active_planets, p1_name, target_7th, "Full Aspect (7th)"))
        
        # 2. Special Aspects
        p_name = p1.name
        if p_name == "Mars":
            # 4th and 8th
            target_4th = (p1_sign_num + 3) % 12
            target_8th = (p1_sign_num + 7) % 12
            aspects.extend(_find_planets_in_sign(subject, active_planets, p1_name, target_4th, "Special 4th Aspect"))
            aspects.extend(_find_planets_in_sign(subject, active_planets, p1_name, target_8th, "Special 8th Aspect"))
            
        elif p_name == "Jupiter":
            # 5th and 9th
            target_5th = (p1_sign_num + 4) % 12
            target_9th = (p1_sign_num + 8) % 12
            aspects.extend(_find_planets_in_sign(subject, active_planets, p1_name, target_5th, "Special 5th Aspect"))
            aspects.extend(_find_planets_in_sign(subject, active_planets, p1_name, target_9th, "Special 9th Aspect"))
            
        elif p_name == "Saturn":
            # 3rd and 10th
            target_3rd = (p1_sign_num + 2) % 12
            target_10th = (p1_sign_num + 9) % 12
            aspects.extend(_find_planets_in_sign(subject, active_planets, p1_name, target_3rd, "Special 3rd Aspect"))
            aspects.extend(_find_planets_in_sign(subject, active_planets, p1_name, target_10th, "Special 10th Aspect"))
            
    return aspects

def _find_planets_in_sign(subject, planet_list, caster_name, target_sign_num, aspect_name) -> List[VedicAspectModel]:
    """Helper to find planets in a target sign and create aspect models."""
    results = []
    p1 = subject[caster_name.lower()]
    
    for p2_name in planet_list:
        if p2_name == caster_name:
            continue
            
        p2 = subject[p2_name.lower()]
        if p2.sign_num == target_sign_num:
            results.append(VedicAspectModel(
                p1_name=caster_name,
                p2_name=p2_name,
                aspect=aspect_name,
                p1_sign=p1.sign,
                p2_sign=p2.sign
            ))
            
    return results
