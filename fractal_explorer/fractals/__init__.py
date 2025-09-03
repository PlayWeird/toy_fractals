"""Fractal implementations module."""

from .base import Fractal, EscapeTimeFractal, IFSFractal
from .escape_time import MandelbrotSet, JuliaSet, BurningShip
from .ifs import SierpinskiTriangle, BarnsleyFern, DragonCurve
from .deterministic_fractals import DeterministicSierpinskiTriangle

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
    "DeterministicSierpinskiTriangle",
]