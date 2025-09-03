"""Escape-time fractal implementations."""

import numpy as np
from numba import jit, prange
from typing import Tuple, Dict, Any, Optional
from .base import EscapeTimeFractal


@jit(nopython=True, parallel=True, cache=True)
def mandelbrot_kernel(xmin: float, xmax: float, ymin: float, ymax: float,
                      width: int, height: int, max_iter: int) -> np.ndarray:
    """Optimized Mandelbrot set computation kernel.
    
    Args:
        xmin, xmax, ymin, ymax: Coordinate bounds
        width, height: Image dimensions
        max_iter: Maximum iterations
        
    Returns:
        2D array of iteration counts
    """
    result = np.zeros((height, width), dtype=np.float32)
    
    dx = (xmax - xmin) / width
    dy = (ymax - ymin) / height
    
    for py in prange(height):
        y = ymin + py * dy
        for px in range(width):
            x = xmin + px * dx
            c = complex(x, y)
            z = 0j
            
            for i in range(max_iter):
                if abs(z) > 2.0:
                    # Smooth coloring
                    result[py, px] = i + 1 - np.log2(np.log2(abs(z)))
                    break
                z = z * z + c
            else:
                result[py, px] = max_iter
                
    return result


@jit(nopython=True, parallel=True, cache=True)
def julia_kernel(xmin: float, xmax: float, ymin: float, ymax: float,
                 width: int, height: int, max_iter: int,
                 c_real: float, c_imag: float) -> np.ndarray:
    """Optimized Julia set computation kernel.
    
    Args:
        xmin, xmax, ymin, ymax: Coordinate bounds
        width, height: Image dimensions
        max_iter: Maximum iterations
        c_real, c_imag: Julia constant components
        
    Returns:
        2D array of iteration counts
    """
    result = np.zeros((height, width), dtype=np.float32)
    c = complex(c_real, c_imag)
    
    dx = (xmax - xmin) / width
    dy = (ymax - ymin) / height
    
    for py in prange(height):
        y = ymin + py * dy
        for px in range(width):
            x = xmin + px * dx
            z = complex(x, y)
            
            for i in range(max_iter):
                if abs(z) > 2.0:
                    # Smooth coloring
                    result[py, px] = i + 1 - np.log2(np.log2(abs(z)))
                    break
                z = z * z + c
            else:
                result[py, px] = max_iter
                
    return result


@jit(nopython=True, parallel=True, cache=True)
def burning_ship_kernel(xmin: float, xmax: float, ymin: float, ymax: float,
                       width: int, height: int, max_iter: int) -> np.ndarray:
    """Optimized Burning Ship fractal computation kernel.
    
    Args:
        xmin, xmax, ymin, ymax: Coordinate bounds
        width, height: Image dimensions
        max_iter: Maximum iterations
        
    Returns:
        2D array of iteration counts
    """
    result = np.zeros((height, width), dtype=np.float32)
    
    dx = (xmax - xmin) / width
    dy = (ymax - ymin) / height
    
    for py in prange(height):
        y = ymin + py * dy
        for px in range(width):
            x = xmin + px * dx
            zr, zi = 0.0, 0.0
            cr, ci = x, y
            
            for i in range(max_iter):
                if zr * zr + zi * zi > 4.0:
                    # Smooth coloring
                    result[py, px] = i + 1 - np.log2(np.log2(np.sqrt(zr*zr + zi*zi)))
                    break
                    
                # Burning Ship iteration: z = (|Re(z)| + i|Im(z)|)^2 + c
                zr_temp = zr * zr - zi * zi + cr
                zi = abs(2.0 * zr * zi) + ci
                zr = abs(zr_temp)
            else:
                result[py, px] = max_iter
                
    return result


class MandelbrotSet(EscapeTimeFractal):
    """The Mandelbrot set fractal."""
    
    def __init__(self):
        """Initialize Mandelbrot set."""
        super().__init__("Mandelbrot Set", max_iter=256)
        
    def compute(self, width: int, height: int, bounds: Tuple[float, float, float, float],
                **params) -> np.ndarray:
        """Compute the Mandelbrot set.
        
        Args:
            width: Width in pixels
            height: Height in pixels
            bounds: (xmin, xmax, ymin, ymax) coordinate bounds
            **params: Additional parameters (max_iter)
            
        Returns:
            2D array of iteration counts
        """
        max_iter = params.get('max_iter', self.max_iter)
        xmin, xmax, ymin, ymax = bounds
        
        # Calculate zoom level for adaptive iterations
        zoom_level = 4.0 / (xmax - xmin)
        if params.get('adaptive_iter', True):
            max_iter = self.adaptive_iterations(zoom_level)
            
        return mandelbrot_kernel(xmin, xmax, ymin, ymax, width, height, max_iter)
    
    def get_default_bounds(self) -> Tuple[float, float, float, float]:
        """Get default viewing bounds."""
        return (-2.5, 1.0, -1.25, 1.25)
    
    def escape_calculation(self, c: np.ndarray, max_iter: int) -> np.ndarray:
        """Not used for optimized kernel implementation."""
        pass
    
    def get_interesting_points(self) -> Dict[str, Tuple[float, float, float]]:
        """Get interesting points to explore.
        
        Returns:
            Dictionary of name -> (center_x, center_y, suggested_zoom)
        """
        return {
            "Main bulb": (0.0, 0.0, 1.0),
            "Seahorse valley": (-0.75, 0.1, 50.0),
            "Elephant valley": (0.275, 0.0, 50.0),
            "Triple spiral": (-0.088, 0.654, 250.0),
            "Mini Mandelbrot": (-1.25, 0.0, 20.0),
            "Dendrite fractal": (-0.74529, 0.11307, 2000.0),
        }


class JuliaSet(EscapeTimeFractal):
    """Julia set fractal with adjustable c parameter."""
    
    def __init__(self, c_real: float = -0.4, c_imag: float = 0.6):
        """Initialize Julia set.
        
        Args:
            c_real: Real component of the Julia constant
            c_imag: Imaginary component of the Julia constant
        """
        super().__init__("Julia Set", max_iter=256)
        self.c_real = c_real
        self.c_imag = c_imag
        
    def compute(self, width: int, height: int, bounds: Tuple[float, float, float, float],
                **params) -> np.ndarray:
        """Compute the Julia set.
        
        Args:
            width: Width in pixels
            height: Height in pixels
            bounds: (xmin, xmax, ymin, ymax) coordinate bounds
            **params: Additional parameters (max_iter, c_real, c_imag)
            
        Returns:
            2D array of iteration counts
        """
        max_iter = params.get('max_iter', self.max_iter)
        c_real = params.get('c_real', self.c_real)
        c_imag = params.get('c_imag', self.c_imag)
        xmin, xmax, ymin, ymax = bounds
        
        return julia_kernel(xmin, xmax, ymin, ymax, width, height, max_iter,
                           c_real, c_imag)
    
    def get_default_bounds(self) -> Tuple[float, float, float, float]:
        """Get default viewing bounds."""
        return (-2.0, 2.0, -1.5, 1.5)
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get adjustable parameters."""
        params = super().get_parameters()
        params.update({
            'c_real': {
                'type': float,
                'default': -0.4,
                'min': -2.0,
                'max': 2.0,
                'step': 0.01,
                'description': 'Real component of Julia constant'
            },
            'c_imag': {
                'type': float,
                'default': 0.6,
                'min': -2.0,
                'max': 2.0,
                'step': 0.01,
                'description': 'Imaginary component of Julia constant'
            }
        })
        return params
    
    def escape_calculation(self, c: np.ndarray, max_iter: int) -> np.ndarray:
        """Not used for optimized kernel implementation."""
        pass
    
    def get_interesting_constants(self) -> Dict[str, Tuple[float, float]]:
        """Get interesting Julia set constants.
        
        Returns:
            Dictionary of name -> (c_real, c_imag)
        """
        return {
            "Dendrite": (-0.8, 0.156),
            "Rabbit": (-0.123, 0.745),
            "Dragon": (-0.4, 0.6),
            "Siegel disk": (-0.391, -0.587),
            "San Marco": (-0.75, 0.0),
            "Glynn": (-0.2, 0.8),
            "Swirl": (0.285, 0.01),
            "Lightning": (-0.8, 0.0),
        }


class BurningShip(EscapeTimeFractal):
    """The Burning Ship fractal."""
    
    def __init__(self):
        """Initialize Burning Ship fractal."""
        super().__init__("Burning Ship", max_iter=256)
        
    def compute(self, width: int, height: int, bounds: Tuple[float, float, float, float],
                **params) -> np.ndarray:
        """Compute the Burning Ship fractal.
        
        Args:
            width: Width in pixels
            height: Height in pixels
            bounds: (xmin, xmax, ymin, ymax) coordinate bounds
            **params: Additional parameters (max_iter)
            
        Returns:
            2D array of iteration counts
        """
        max_iter = params.get('max_iter', self.max_iter)
        xmin, xmax, ymin, ymax = bounds
        
        # Calculate zoom level for adaptive iterations
        zoom_level = 4.0 / (xmax - xmin)
        if params.get('adaptive_iter', True):
            max_iter = self.adaptive_iterations(zoom_level)
            
        return burning_ship_kernel(xmin, xmax, ymin, ymax, width, height, max_iter)
    
    def get_default_bounds(self) -> Tuple[float, float, float, float]:
        """Get default viewing bounds."""
        return (-2.5, 1.5, -2.0, 1.0)
    
    def escape_calculation(self, c: np.ndarray, max_iter: int) -> np.ndarray:
        """Not used for optimized kernel implementation."""
        pass
    
    def get_interesting_points(self) -> Dict[str, Tuple[float, float, float]]:
        """Get interesting points to explore.
        
        Returns:
            Dictionary of name -> (center_x, center_y, suggested_zoom)
        """
        return {
            "Main ship": (-0.5, -0.5, 1.0),
            "Armada": (-1.755, -0.03, 100.0),
            "Hidden ship": (-1.755, -0.028, 1000.0),
            "Antenna": (-1.625, 0.0, 50.0),
        }