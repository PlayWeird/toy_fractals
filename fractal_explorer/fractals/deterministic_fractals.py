"""Deterministic fractal implementations for consistent behavior."""

import numpy as np
from numba import jit, prange
from typing import Tuple, Dict, Any
from .base import Fractal


@jit(nopython=True, parallel=True, cache=True)
def sierpinski_escape_time(xmin: float, xmax: float, ymin: float, ymax: float,
                          width: int, height: int, max_iter: int) -> np.ndarray:
    """Deterministic Sierpinski Triangle using escape-time algorithm.
    
    This creates a consistent, deterministic fractal that doesn't change
    between renders and maintains structure at all zoom levels.
    """
    result = np.zeros((height, width), dtype=np.float32)
    
    dx = (xmax - xmin) / width
    dy = (ymax - ymin) / height
    
    for py in prange(height):
        y = ymin + py * dy
        for px in range(width):
            x = xmin + px * dx
            
            # Sierpinski Triangle test: point is in the triangle if
            # the binary representation of floor coordinates has no
            # overlapping 1 bits
            if x < 0 or y < 0 or x > 1 or y > 1:
                result[py, px] = 0
                continue
            
            # Scale to integer coordinates for binary test
            scale = 2**max_iter
            ix = int(x * scale)
            iy = int(y * scale)
            
            # Sierpinski test: point is in fractal if ix & iy == 0
            # This gives the characteristic triangular holes
            iterations = 0
            temp_x, temp_y = ix, iy
            
            for i in range(max_iter):
                if temp_x & temp_y:
                    iterations = i
                    break
                temp_x >>= 1
                temp_y >>= 1
            else:
                iterations = max_iter
                
            # Normalize result
            result[py, px] = iterations / max_iter
                
    return result


class DeterministicSierpinskiTriangle(Fractal):
    """Deterministic Sierpinski Triangle that maintains structure when zoomed."""
    
    def __init__(self):
        """Initialize deterministic Sierpinski Triangle."""
        super().__init__("Sierpinski Triangle (Deterministic)")
        self.max_iter = 16
        
    def compute(self, width: int, height: int, bounds: Tuple[float, float, float, float],
                **params) -> np.ndarray:
        """Compute deterministic Sierpinski Triangle.
        
        Args:
            width: Width in pixels
            height: Height in pixels
            bounds: (xmin, xmax, ymin, ymax) coordinate bounds
            **params: Additional parameters (max_iter)
            
        Returns:
            2D array representing the fractal
        """
        max_iter = params.get('max_iter', self.max_iter)
        xmin, xmax, ymin, ymax = bounds
        
        # Calculate zoom level for adaptive iterations
        zoom_level = 1.2 / (xmax - xmin)
        if params.get('adaptive_iter', True):
            max_iter = min(max_iter + int(np.log2(max(1, zoom_level))), 24)
        
        return sierpinski_escape_time(xmin, xmax, ymin, ymax, width, height, max_iter)
    
    def get_default_bounds(self) -> Tuple[float, float, float, float]:
        """Get default viewing bounds."""
        return (-0.1, 1.1, -0.1, 1.0)
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get adjustable parameters."""
        return {
            'max_iter': {
                'type': int,
                'default': 16,
                'min': 8,
                'max': 24,
                'step': 1,
                'description': 'Detail Level'
            }
        }
    
    def get_type(self) -> str:
        """Get fractal type."""
        return 'escape_time'


@jit(nopython=True, parallel=True, cache=True)
def sierpinski_chaos_game_deterministic(width: int, height: int, 
                                       bounds: Tuple[float, float, float, float],
                                       seed: int = 42) -> np.ndarray:
    """Deterministic chaos game for Sierpinski Triangle with fixed seed.
    
    This version uses a deterministic sequence instead of random numbers,
    ensuring the fractal looks the same every time.
    """
    xmin, xmax, ymin, ymax = bounds
    result = np.zeros((height, width), dtype=np.float32)
    
    # Triangle vertices in normalized coordinates
    vertices = np.array([
        [0.5, 0.866],   # Top
        [0.0, 0.0],     # Bottom left  
        [1.0, 0.0]      # Bottom right
    ])
    
    # Starting point
    x, y = 0.5, 0.5
    
    # Use deterministic sequence instead of random
    # This ensures consistent results
    iterations = 1000000
    
    # Simple deterministic sequence generator (linear congruential)
    rng_state = seed
    
    for i in range(iterations):
        # Generate deterministic "random" choice
        rng_state = (rng_state * 1664525 + 1013904223) % (2**32)
        choice = rng_state % 3
        
        # Move halfway to chosen vertex
        target_x, target_y = vertices[choice]
        x = (x + target_x) * 0.5
        y = (y + target_y) * 0.5
        
        # Skip initial iterations for settling
        if i < 1000:
            continue
            
        # Map to pixel coordinates
        px = int((x - xmin) / (xmax - xmin) * (width - 1))
        py = int((y - ymin) / (ymax - ymin) * (height - 1))
        
        if 0 <= px < width and 0 <= py < height:
            result[height - 1 - py, px] += 1
    
    # Normalize
    if result.max() > 0:
        result = np.log1p(result)
        result = result / result.max()
        
    return result


class DeterministicSierpinskiChaos(Fractal):
    """Sierpinski Triangle using deterministic chaos game."""
    
    def __init__(self):
        """Initialize deterministic chaos game Sierpinski."""
        super().__init__("Sierpinski Triangle (Chaos Game)")
        
    def compute(self, width: int, height: int, bounds: Tuple[float, float, float, float],
                **params) -> np.ndarray:
        """Compute Sierpinski using deterministic chaos game."""
        # Use bounds as seed for consistency - same zoom area = same result
        seed = hash(str(bounds)) % (2**31)
        return sierpinski_chaos_game_deterministic(width, height, bounds, seed)
    
    def get_default_bounds(self) -> Tuple[float, float, float, float]:
        """Get default viewing bounds."""
        return (-0.1, 1.1, -0.1, 1.0)
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get adjustable parameters."""
        return {}
    
    def get_type(self) -> str:
        """Get fractal type."""
        return 'deterministic'