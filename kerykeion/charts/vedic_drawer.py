# -*- coding: utf-8 -*-
"""
Vedic Chart Drawers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, TYPE_CHECKING
import logging
from kerykeion.schemas.kr_models import DualChartDataModel
from kerykeion.schemas.vedic_settings_models import VedicChartConfigModel
from kerykeion.charts.vedic_geometry_utils import VedicGeometryUtils

if TYPE_CHECKING:
    from kerykeion.schemas.kr_models import ChartDataModel

logger = logging.getLogger(__name__)

class BaseVedicDrawer(ABC):
    """
    Base class for Vedic chart drawers.
    """
    def __init__(self, chart_data: "ChartDataModel", config: VedicChartConfigModel = None):
        self.chart_data = chart_data
        self.config = config or VedicChartConfigModel()

        if isinstance(chart_data, DualChartDataModel):
            self.subject = chart_data.first_subject
        else:
            # SingleChartDataModel
            self.subject = chart_data.subject


        # Mapping of internal names to symbol IDs in the template
        self.point_to_symbol = {
            "Sun": "Sun",
            "Moon": "Moon",
            "Mercury": "Mercury",
            "Venus": "Venus",
            "Mars": "Mars",
            "Jupiter": "Jupiter",
            "Saturn": "Saturn",
            "Uranus": "Uranus",
            "Neptune": "Neptune",
            "Pluto": "Pluto",
            "Chiron": "Chiron",
            "Mean_Lilith": "Mean_Lilith",
            "Mean_North_Lunar_Node": "Mean_North_Lunar_Node",
            "True_North_Lunar_Node": "True_North_Lunar_Node",
            "Mean_South_Lunar_Node": "Mean_South_Lunar_Node",
            "True_South_Lunar_Node": "True_South_Lunar_Node",
            "Ascendant": "Ascendant",
            # Add others as needed
        }

    @abstractmethod
    def generate_svg_string(self) -> str:
        """Generates the SVG string for the chart."""
        pass

    def _get_svg_header(self) -> str:
        defs = self._get_symbols_defs()
        return (
            f'<svg width="{self.config.width}" height="{self.config.height}" '
            f'viewBox="0 0 {self.config.width} {self.config.height}" '
            f'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
            f'<rect width="100%" height="100%" fill="{self.config.background_color}" />'
            f'{defs}'
            f'<style>'
            f':root {{'
            f'--kerykeion-chart-color-sun: {self.config.planet_color};'
            f'--kerykeion-chart-color-moon: {self.config.planet_color};'
            f'--kerykeion-chart-color-mercury: {self.config.planet_color};'
            f'--kerykeion-chart-color-venus: {self.config.planet_color};'
            f'--kerykeion-chart-color-mars: {self.config.planet_color};'
            f'--kerykeion-chart-color-jupiter: {self.config.planet_color};'
            f'--kerykeion-chart-color-saturn: {self.config.planet_color};'
            f'--kerykeion-chart-color-uranus: {self.config.planet_color};'
            f'--kerykeion-chart-color-neptune: {self.config.planet_color};'
            f'--kerykeion-chart-color-pluto: {self.config.planet_color};'
            f'--kerykeion-chart-color-chiron: {self.config.planet_color};'
            f'--kerykeion-chart-color-mean-lilith: {self.config.planet_color};'
            f'--kerykeion-chart-color-mean-node: {self.config.planet_color};'
            f'--kerykeion-chart-color-true-node: {self.config.planet_color};'
            f'--kerykeion-chart-color-first-house: {self.config.planet_color};'
            f'--kerykeion-chart-color-tenth-house: {self.config.planet_color};'
            f'--kerykeion-chart-color-seventh-house: {self.config.planet_color};'
            f'--kerykeion-chart-color-fourth-house: {self.config.planet_color};'
            f'}}'
            f'</style>'
        )

    def _get_symbols_defs(self) -> str:
        """
        Extracts symbols definitions from the main chart template.
        """
        try:
            from pathlib import Path
            template_path = Path(__file__).parent / "templates" / "chart.xml"
            content = template_path.read_text(encoding="utf-8")
            start_tag = "<defs>"
            end_tag = "</defs>"
            start_idx = content.find(start_tag)
            end_idx = content.find(end_tag) + len(end_tag)
            if start_idx != -1 and end_idx != -1:
                return content[start_idx:end_idx]
        except Exception as e:
            logger.error(f"Failed to load symbols from template: {e}")

        return "<defs></defs>"

    def _get_svg_footer(self) -> str:
        return "</svg>"

    def _draw_grid(self, paths: List[str]) -> str:
        svg = f'<g stroke="{self.config.line_color}" stroke-width="{self.config.line_width}" fill="none">'
        for path in paths:
            svg += f'<path d="{path}" />'
        svg += '</g>'
        return svg

    def _draw_point(self, name: str, x: float, y: float, scale: float = 0.5) -> str:
        symbol_id = self.point_to_symbol.get(name, name)
        # Offset to center the symbol (symbols are roughly 24x24)
        offset = -12 * scale
        return (
            f'<g transform="translate({x + offset}, {y + offset}) scale({scale})">'
            f'<use xlink:href="#{symbol_id}" />'
            f'</g>'
        )

    def _get_point_label(self, name: str) -> str:
        # Simple abbreviation for now
        labels = {
            "Sun": "Su", "Moon": "Mo", "Mercury": "Me", "Venus": "Ve",
            "Mars": "Ma", "Jupiter": "Ju", "Saturn": "Sa", "Rahu": "Ra",
            "Ketu": "Ke", "Ascendant": "As", "Lagna": "Lg"
        }
        return labels.get(name, name[:2])

    def _get_house_num(self, house_name: str) -> int:
        """Maps house name string to its number (1-12)."""
        house_map = {
            "First_House": 1, "Second_House": 2, "Third_House": 3, "Fourth_House": 4,
            "Fifth_House": 5, "Sixth_House": 6, "Seventh_House": 7, "Eighth_House": 8,
            "Ninth_House": 9, "Tenth_House": 10, "Eleventh_House": 11, "Twelfth_House": 12
        }
        return house_map.get(house_name, 1)

class NorthIndianDrawer(BaseVedicDrawer):
    """
    Drawer for North Indian (Diamond) style Vedic charts.
    """
    def generate_svg_string(self) -> str:
        paths = VedicGeometryUtils.get_north_indian_grid_paths(
            self.config.width, self.config.height, self.config.padding
        )
        centers = VedicGeometryUtils.get_north_indian_house_centers(
            self.config.width, self.config.height, self.config.padding
        )

        svg = self._get_svg_header()
        svg += self._draw_grid(paths)

        # Group planets by house
        houses: Dict[int, List[str]] = {i: [] for i in range(1, 13)}

        # Get Ascendant house number to calculate signs in houses
        # In North Indian, 1st house is always at the top, but the sign number inside changes.
        lagna_sign_num = self.subject.ascendant.sign_num + 1

        for i in range(12):
            sign_in_house = (lagna_sign_num + i - 1) % 12 + 1
            hx, hy = centers[i]
            if self.config.show_labels:
                svg += f'<text x="{hx}" y="{hy + 15}" font-size="10" fill="{self.config.label_color}" text-anchor="middle">{sign_in_house}</text>'

        # Place planets
        for point_name in self.chart_data.active_points:
            point = self.subject.get(point_name.lower())
            if point and point.house:
                house_num = self._get_house_num(point.house)
                houses[house_num].append(point_name)

        for house_num, points in houses.items():
            hx, hy = centers[house_num - 1]
            for i, p_name in enumerate(points):
                # Simple layout within the house triangle
                px = hx + (i % 2 - 0.5) * 20
                py = hy + (i // 2 - 0.5) * 20
                svg += self._draw_point(p_name, px, py)

        svg += self._get_svg_footer()
        return svg

class SouthIndianDrawer(BaseVedicDrawer):
    """
    Drawer for South Indian (Grid) style Vedic charts.
    """
    def generate_svg_string(self) -> str:
        paths = VedicGeometryUtils.get_south_indian_grid_paths(
            self.config.width, self.config.height, self.config.padding
        )
        centers = VedicGeometryUtils.get_south_indian_sign_centers(
            self.config.width, self.config.height, self.config.padding
        )

        svg = self._get_svg_header()
        svg += self._draw_grid(paths)

        # Signs are fixed in South Indian: Aries is index 0 in centers
        signs: Dict[int, List[str]] = {i: [] for i in range(1, 13)}

        # Mark Ascendant
        lagna_sign_num = self.subject.ascendant.sign_num + 1
        lx, ly = centers[lagna_sign_num - 1]
        svg += f'<text x="{lx - 20}" y="{ly - 20}" font-size="12" fill="{self.config.label_color}" font-weight="bold">As</text>'

        for point_name in self.chart_data.active_points:
            point = self.subject.get(point_name.lower())
            if point:
                sign_num = point.sign_num + 1
                signs[sign_num].append(point_name)

        for sign_num, points in signs.items():
            sx, sy = centers[sign_num - 1]
            for i, p_name in enumerate(points):
                px = sx + (i % 2 - 0.5) * 25
                py = sy + (i // 2 - 0.5) * 25
                svg += self._draw_point(p_name, px, py)

        svg += self._get_svg_footer()
        return svg
