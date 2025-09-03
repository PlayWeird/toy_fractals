"""Fractal implementations module."""

from .base import Fractal, EscapeTimeFractal, IFSFractal
from .escape_time import MandelbrotSet, JuliaSet, BurningShip
from .ifs import SierpinskiTriangle, BarnsleyFern, DragonCurve

__all__ = [
    "Fractal",
    "EscapeTimeFractal", 
    "IFSFractal",
    "MandelbrotSet",
    "JuliaSet",
    "BurningShip",
    "SierpinskiTriangle",
    "BarnsleyFern",
    "DragonCurve",
]