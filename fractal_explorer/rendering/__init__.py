"""Rendering and visualization module."""

from .colormaps import ColorMapper, get_available_palettes
from .renderer_2d import FractalRenderer2D

__all__ = [
    "ColorMapper",
    "FractalRenderer2D",
    "get_available_palettes"
]