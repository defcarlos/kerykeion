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
            "Medium_Coeli": "Medium_Coeli",
            "Descendant": "Descendant",
            "Imum_Coeli": "Imum_Coeli",
            # Signs
            "Aries": "Aries", "Taurus": "Taurus", "Gemini": "Gemini", "Cancer": "Cancer",
            "Leo": "Leo", "Virgo": "Virgo", "Libra": "Libra", "Scorpio": "Scorpio",
            "Sagittarius": "Sagittarius", "Capricorn": "Capricorn", "Aquarius": "Aquarius", "Pisces": "Pisces"
        }
        
        self.sign_names = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]

    @abstractmethod
    def generate_svg_string(self) -> str:
        """Generates the SVG string for the chart."""
        pass

    def _get_svg_header(self) -> str:
        defs = self._get_symbols_defs()
        theme_css = self._get_theme_css()

        return (
            f"<!-- Kerykeion Vedic Chart -->\n"
            f'<svg width="{self.config.width}" height="{self.config.height}" '
            f'viewBox="0 0 {self.config.width} {self.config.height}" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'xmlns:kr="https://www.kerykeion.net/">\n'
            f"<style>{theme_css}</style>\n"
            f'<rect width="100%" height="100%" fill="var(--kerykeion-chart-color-paper-1)" />\n'
            f"{defs}\n"
        )

    def _get_theme_css(self) -> str:
        """Loads CSS for the selected theme."""
        theme_name = self.config.theme or "classic"

        try:
            from pathlib import Path
            theme_path = Path(__file__).parent / "themes" / f"{theme_name}.css"
            if theme_path.exists():
                return theme_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to load theme CSS: {e}")

        return ""

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
        style = (
            "fill: none; "
            "stroke: var(--kerykeion-chart-color-houses-radix-line); "
            f"stroke-width: {self.config.line_width}px;"
        )
        svg = f'<g kr:node="Chart_Grid" style="{style}">\n'
        for path in paths:
            svg += f'  <path d="{path}" />\n'
        svg += "</g>\n"
        return svg

    def _draw_backgrounds(self, polygons: List[List[tuple[float, float]]], sign_nums: List[int]) -> str:
        """
        Draws colored background fills for houses/boxes.
        sign_nums: 1-12 for each polygon.
        """
        svg = '<g kr:node="Chart_Background_Fills" style="fill-opacity: 0.15; stroke: none;">\n'
        for i, poly in enumerate(polygons):
            points_str = " ".join([f"{p[0]},{p[1]}" for p in poly])
            sign_idx = sign_nums[i] - 1
            color = f"var(--kerykeion-chart-color-zodiac-bg-{sign_idx})"
            svg += f'  <polygon points="{points_str}" style="fill: {color};" />\n'
        svg += "</g>\n"
        return svg

    def _draw_point(self, name: str, x: float, y: float, scale: float = 1.0) -> str:
        symbol_id = self.point_to_symbol.get(name, name)
        offset = -12 * scale
        return (
            f'  <g transform="translate({x + offset}, {y + offset}) scale({scale})">\n'
            f'    <use xlink:href="#{symbol_id}" />\n'
            f"  </g>\n"
        )

    def _draw_sign_glyph(self, sign_num: int, x: float, y: float, scale: float = 0.4, opacity: float = 1.0) -> str:
        """
        Draws a sign glyph with theme color.
        """
        sign_idx = sign_num - 1
        name = self.sign_names[sign_idx]
        symbol_id = self.point_to_symbol.get(name, name)
        offset = -12 * scale
        color = f"var(--kerykeion-chart-color-zodiac-icon-{sign_idx})"
        
        style = f"fill: {color}; fill-opacity: {opacity};"
        
        return (
            f'  <g transform="translate({x + offset}, {y + offset}) scale({scale})" style="{style}">\n'
            f'    <use xlink:href="#{symbol_id}" />\n'
            f"  </g>\n"
        )

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
        w, h, p = self.config.width, self.config.height, self.config.padding
        paths = VedicGeometryUtils.get_north_indian_grid_paths(w, h, p)
        centers = VedicGeometryUtils.get_north_indian_house_centers(w, h, p)
        polygons = VedicGeometryUtils.get_north_indian_house_polygons(w, h, p)

        # Calculate signs in each house
        lagna_sign_num = self.subject.ascendant.sign_num + 1
        house_sign_nums = [(lagna_sign_num + i - 1) % 12 + 1 for i in range(12)]

        svg = self._get_svg_header()
        
        # Draw background fills
        svg += self._draw_backgrounds(polygons, house_sign_nums)
        
        # Draw grid
        svg += self._draw_grid(paths)

        # Mark 1st house
        hx, hy = centers[0]
        lagna_marker_style = (
            "fill: var(--kerykeion-chart-color-first-house); "
            "font-size: 16px; "
            "font-family: sans-serif; "
            "text-anchor: middle; "
            "font-weight: bold;"
        )
        svg += f'  <text x="{hx}" y="{hy - 15}" style="{lagna_marker_style}">As</text>\n'

        # Draw sign glyphs
        if self.config.show_labels:
            for i in range(12):
                hx, hy = centers[i]
                svg += self._draw_sign_glyph(house_sign_nums[i], hx, hy + 22, scale=0.5)

        # Group planets by house
        houses: Dict[int, List[str]] = {i: [] for i in range(1, 13)}
        for point_name in self.chart_data.active_points:
            if point_name == "Ascendant": continue
            point = self.subject.get(point_name.lower())
            if point and point.house:
                houses[self._get_house_num(point.house)].append(point_name)

        for house_num, points in houses.items():
            hx, hy = centers[house_num - 1]
            for i, p_name in enumerate(points):
                px = hx + (i % 2 - 0.5) * 32
                py = hy + (i // 2 - 0.5) * 32
                svg += self._draw_point(p_name, px, py)

        svg += self._get_svg_footer()
        return svg

class SouthIndianDrawer(BaseVedicDrawer):
    """
    Drawer for South Indian (Grid) style Vedic charts.
    """
    def generate_svg_string(self) -> str:
        w, h, p = self.config.width, self.config.height, self.config.padding
        paths = VedicGeometryUtils.get_south_indian_grid_paths(w, h, p)
        centers = VedicGeometryUtils.get_south_indian_sign_centers(w, h, p)
        polygons = VedicGeometryUtils.get_south_indian_sign_polygons(w, h, p)

        svg = self._get_svg_header()
        
        # Draw background fills (Signs 1-12 are fixed in South Indian)
        svg += self._draw_backgrounds(polygons, list(range(1, 13)))
        
        # Draw grid
        svg += self._draw_grid(paths)

        # Signs are fixed: Aries is index 0
        lagna_sign_num = self.subject.ascendant.sign_num + 1
        lx, ly = centers[lagna_sign_num - 1]
        
        lagna_style = (
            "fill: var(--kerykeion-chart-color-first-house); "
            "font-size: 22px; "
            "font-family: sans-serif; "
            "font-weight: bold;"
        )
        svg += f'  <text x="{lx - 25}" y="{ly - 18}" style="{lagna_style}">As</text>\n'

        # Draw educational sign glyphs in corners
        for i in range(12):
            sx, sy = centers[i]
            # Offset to top-left of the box (box is cw x ch)
            cw, ch = (w - 2 * p) / 4, (h - 2 * p) / 4
            bx, by = sx - cw / 2 + 15, sy - ch / 2 + 15
            svg += self._draw_sign_glyph(i + 1, bx, by, scale=0.3, opacity=0.6)

        # Place planets
        signs_planets: Dict[int, List[str]] = {i: [] for i in range(1, 13)}
        for point_name in self.chart_data.active_points:
            if point_name == "Ascendant": continue
            point = self.subject.get(point_name.lower())
            if point:
                signs_planets[point.sign_num + 1].append(point_name)

        for sign_num, points in signs_planets.items():
            sx, sy = centers[sign_num - 1]
            for i, p_name in enumerate(points):
                px = sx + (i % 2 - 0.5) * 38
                py = sy + (i // 2 - 0.5) * 38
                svg += self._draw_point(p_name, px, py)

        svg += self._get_svg_footer()
        return svg
