# -*- coding: utf-8 -*-
"""
Varga (Divisional Charts) Factory
=================================

This module provides the VargaFactory class for calculating Vedic divisional
charts (Saptavarga) from an AstrologicalSubjectModel.

The Saptavarga includes:
- D1: Rasi (Standard)
- D2: Hora
- D3: Drekkana
- D7: Saptamsha
- D9: Navamsha
- D12: Dwadashamsha
- D30: Trimshamsha

Mathematical logic follows the standard Parashari rules.

This is part of Kerykeion (C) 2025 Giacomo Battaglia
"""

from typing import Dict, List, Optional, Union
from kerykeion.schemas import (
    AstrologicalSubjectModel,
    VargaChartModel,
    VargaPointModel,
    KerykeionPointModel,
    AstrologicalPoint,
)
from kerykeion.utilities import get_kerykeion_point_from_degree
from kerykeion.vedic_utils import get_vedic_dignity, get_sign_lord, is_pushkara
from kerykeion.western_utils import get_western_dignity


class VargaFactory:
    """
    Factory class for calculating divisional (Varga) charts.
    """

    def __init__(self, subject: AstrologicalSubjectModel):
        self.subject = subject

    def calculate_saptavarga(self) -> Dict[str, VargaChartModel]:
        """
        Calculate the standard 7 divisional charts (Saptavarga).

        Returns:
            Dict[str, VargaChartModel]: Collection of divisional charts.
        """
        vargas = {}
        varga_types = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]

        for vt in varga_types:
            vargas[vt] = self.calculate_varga(vt)

        return vargas

    def calculate_varga(self, varga_type: str) -> VargaChartModel:
        """
        Calculate a specific divisional chart.

        Args:
            varga_type: Type of Varga chart (e.g., 'D9').

        Returns:
            VargaChartModel: The calculated divisional chart.
        """
        points = {}
        active_points = self.subject.active_points

        for point_name in active_points:
            point_data = self.subject[point_name.lower()]
            if point_data:
                varga_point = self._calculate_point_varga(point_data, varga_type)
                points[point_name.lower()] = varga_point

        return VargaChartModel(varga_type=varga_type, points=points)

    def _calculate_point_varga(self, point: KerykeionPointModel, varga_type: str) -> VargaPointModel:
        """
        Calculate the position of a single point in a specific Varga.
        """
        abs_pos = point.abs_pos
        sign_num = point.sign_num
        degree_in_sign = point.position

        varga_sign_num = 0

        if varga_type == "D1":
            varga_sign_num = sign_num

        elif varga_type == "D2":  # Hora
            is_odd = sign_num % 2 == 0  # 0=Ari (Odd), 1=Tau (Even)
            if is_odd:
                varga_sign_num = 4 if degree_in_sign < 15 else 3  # Leo / Cancer
            else:
                varga_sign_num = 3 if degree_in_sign < 15 else 4  # Cancer / Leo

        elif varga_type == "D3":  # Drekkana
            decan = int(degree_in_sign / 10)
            varga_sign_num = (sign_num + (decan * 4)) % 12

        elif varga_type == "D7":  # Saptamsha
            part = int(degree_in_sign / (30 / 7))
            if sign_num % 2 == 0:  # Odd sign
                varga_sign_num = (sign_num + part) % 12
            else:  # Even sign
                varga_sign_num = (sign_num + 6 + part) % 12

        elif varga_type == "D9":  # Navamsha
            part = int(degree_in_sign / (30 / 9))
            start_signs = [0, 9, 6, 3]  # Ari, Cap, Lib, Can
            start_sign = start_signs[sign_num % 4]
            varga_sign_num = (start_sign + part) % 12

        elif varga_type == "D12":  # Dwadashamsha
            part = int(degree_in_sign / 2.5)
            varga_sign_num = (sign_num + part) % 12

        elif varga_type == "D30":  # Trimshamsha
            if sign_num % 2 == 0:  # Odd sign
                if degree_in_sign < 5: varga_sign_num = 0     # Ari (Mars)
                elif degree_in_sign < 10: varga_sign_num = 10 # Aqu (Saturn)
                elif degree_in_sign < 18: varga_sign_num = 8  # Sag (Jupiter)
                elif degree_in_sign < 25: varga_sign_num = 2  # Gem (Mercury)
                else: varga_sign_num = 6                      # Lib (Venus)
            else:  # Even sign
                if degree_in_sign < 5: varga_sign_num = 1     # Tau (Venus)
                elif degree_in_sign < 12: varga_sign_num = 5  # Vir (Mercury)
                elif degree_in_sign < 20: varga_sign_num = 11 # Pis (Jupiter)
                elif degree_in_sign < 25: varga_sign_num = 9  # Cap (Saturn)
                else: varga_sign_num = 7                      # Sco (Mars)

        # Reconstruct full position for the Varga Sign
        # For simplicity, we keep the original absolute position or a normalized one.
        # Vedic practitioners often just care about the sign.
        # Here we project the point into the first degree of the target sign
        # or calculate the relative position within the Varga.
        
        # Calculate the degree within the Varga sign
        divisor = float(varga_type[1:]) if varga_type != "D1" else 1.0
        if varga_type == "D30":
            # Trimshamsha has uneven divisions, so we just set it to 0 or something meaningful
            # for now let's just use the start of the sign.
            varga_degree = 0.0
        else:
            varga_degree = (degree_in_sign * divisor) % 30
            
        varga_abs_pos = (varga_sign_num * 30) + varga_degree

        # Use utility to get full model
        base_point = get_kerykeion_point_from_degree(
            degree=varga_abs_pos,
            name=point.name,
            point_type=point.point_type,
        )
        
        # Enrichments
        sign_lord = get_sign_lord(varga_sign_num)
        is_vargottama_status = (varga_sign_num == sign_num) if varga_type != "D1" else False
        is_pushkara_status = is_pushkara(sign_num, degree_in_sign, varga_type)

        return VargaPointModel(
            **base_point.model_dump(),
            varga_type=varga_type,
            sign_lord=sign_lord,
            is_vargottama=is_vargottama_status,
            is_pushkara=is_pushkara_status,
        )
