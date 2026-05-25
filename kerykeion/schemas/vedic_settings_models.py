# -*- coding: utf-8 -*-
"""
Vedic Chart Configuration Models
"""

from pydantic import Field
from typing import Literal
from kerykeion.schemas.kr_models import SubscriptableBaseModel
from kerykeion.schemas.kr_literals import KerykeionChartTheme

class VedicChartConfigModel(SubscriptableBaseModel):
    """
    Configuration model for Vedic chart visualizations.
    """
    theme: KerykeionChartTheme = Field(default="classic", description="Visual theme for the chart")
    perspective: Literal["Lagna", "Chandra", "Surya"] = Field(
        default="Lagna", description="The reference point for the 1st house"
    )
    width: int = Field(default=600, description="Width of the SVG canvas")
    height: int = Field(default=600, description="Height of the SVG canvas")
    line_color: str = Field(default="#000000", description="Color of the grid lines")
    line_width: float = Field(default=1.5, description="Width of the grid lines")
    font_size: int = Field(default=14, description="Font size for planet symbols and labels")
    background_color: str = Field(default="#FFFFFF", description="Background color of the chart")
    show_labels: bool = Field(default=True, description="Whether to show sign/house labels")
    planet_color: str = Field(default="#000000", description="Color of the planet symbols")
    label_color: str = Field(default="#555555", description="Color of the labels (sign/house numbers)")
    padding: int = Field(default=20, description="Padding around the chart grid")
    zodiac_glyph_scale: float = Field(default=0.8, description="Scale for zodiac sign glyphs")
