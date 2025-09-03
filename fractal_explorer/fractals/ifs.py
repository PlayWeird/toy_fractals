"""Iterated Function System (IFS) fractal implementations."""

import numpy as np
from numba import jit
from typing import Tuple, Dict, Any, List, Callable
from .base import IFSFractal


class SierpinskiTriangle(IFSFractal):
    """Sierpinski Triangle fractal using IFS."""
    
    def __init__(self):
        """Initialize Sierpinski Triangle."""
        super().__init__("Sierpinski Triangle", iterations=200000)
        
    def get_transforms(self) -> List[Tuple[Callable, float]]:
        """Get the transformation functions for Sierpinski Triangle.
        
        Returns:
            List of (transform_function, probability) tuples
        """
        def transform1(x: float, y: float) -> Tuple[float, float]:
            return 0.5 * x, 0.5 * y
        
        def transform2(x: float, y: float) -> Tuple[float, float]:
            return 0.5 * x + 0.5, 0.5 * y
        
        def transform3(x: float, y: float) -> Tuple[float, float]:
            return 0.5 * x + 0.25, 0.5 * y + 0.433
        
        return [
            (transform1, 1.0/3.0),
            (transform2, 1.0/3.0),
            (transform3, 1.0/3.0)
        ]
    
    def get_default_bounds(self) -> Tuple[float, float, float, float]:
        """Get default viewing bounds."""
        return (-0.1, 1.1, -0.1, 1.0)
    
    def compute(self, width: int, height: int, bounds: Tuple[float, float, float, float],
                **params) -> np.ndarray:
        """Compute Sierpinski Triangle using optimized method.
        
        Args:
            width: Width in pixels
            height: Height in pixels
            bounds: (xmin, xmax, ymin, ymax) coordinate bounds
            **params: Additional parameters
            
        Returns:
            2D array representing the fractal
        """
        iterations = params.get('iterations', self.iterations)
        return compute_sierpinski(width, height, bounds, iterations)


@jit(nopython=True)
def compute_sierpinski(width: int, height: int, bounds: Tuple[float, float, float, float],
                       iterations: int) -> np.ndarray:
    """Optimized Sierpinski Triangle computation.
    
    Args:
        width: Width in pixels
        height: Height in pixels
        bounds: Coordinate bounds
        iterations: Number of iterations
        
    Returns:
        2D array of the fractal
    """
    xmin, xmax, ymin, ymax = bounds
    result = np.zeros((height, width), dtype=np.float32)
    
    # Starting point
    x, y = 0.5, 0.5
    
    # Skip first iterations
    skip = min(100, iterations // 100)
    
    for i in range(iterations + skip):
        # Random choice between 3 transforms (equal probability)
        choice = np.random.randint(0, 3)
        
        if choice == 0:
            x, y = 0.5 * x, 0.5 * y
        elif choice == 1:
            x, y = 0.5 * x + 0.5, 0.5 * y
        else:
            x, y = 0.5 * x + 0.25, 0.5 * y + 0.433
        
        if i < skip:
            continue
            
        # Map to pixel coordinates with anti-aliasing
        fx = (x - xmin) / (xmax - xmin) * (width - 1)
        fy = (y - ymin) / (ymax - ymin) * (height - 1)
        
        px = int(fx)
        py = int(fy)
        
        # Apply anti-aliasing with bilinear interpolation
        if 0 <= px < width-1 and 0 <= py < height-1:
            dx = fx - px
            dy = fy - py
            w00 = (1 - dx) * (1 - dy)
            w10 = dx * (1 - dy)
            w01 = (1 - dx) * dy
            w11 = dx * dy
            
            result[height - 1 - py, px] += w00
            result[height - 1 - py, px + 1] += w10
            result[height - 1 - (py + 1), px] += w01
            result[height - 1 - (py + 1), px + 1] += w11
        elif 0 <= px < width and 0 <= py < height:
            result[height - 1 - py, px] += 1
    
    # Normalize
    if result.max() > 0:
        result = np.log1p(result)
        result = result / result.max()
        
    return result


class BarnsleyFern(IFSFractal):
    """Barnsley Fern fractal using IFS."""
    
    def __init__(self):
        """Initialize Barnsley Fern."""
        super().__init__("Barnsley Fern", iterations=1000000)
        
    def get_transforms(self) -> List[Tuple[Callable, float]]:
        """Get the transformation functions for Barnsley Fern.
        
        Returns:
            List of (transform_function, probability) tuples
        """
        def transform1(x: float, y: float) -> Tuple[float, float]:
            return 0.0, 0.16 * y
        
        def transform2(x: float, y: float) -> Tuple[float, float]:
            return 0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6
        
        def transform3(x: float, y: float) -> Tuple[float, float]:
            return 0.2 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6
        
        def transform4(x: float, y: float) -> Tuple[float, float]:
            return -0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44
        
        return [
            (transform1, 0.01),
            (transform2, 0.85),
            (transform3, 0.07),
            (transform4, 0.07)
        ]
    
    def get_default_bounds(self) -> Tuple[float, float, float, float]:
        """Get default viewing bounds."""
        return (-3.0, 3.0, -0.5, 10.5)
    
    def compute(self, width: int, height: int, bounds: Tuple[float, float, float, float],
                **params) -> np.ndarray:
        """Compute Barnsley Fern using optimized method.
        
        Args:
            width: Width in pixels
            height: Height in pixels
            bounds: (xmin, xmax, ymin, ymax) coordinate bounds
            **params: Additional parameters
            
        Returns:
            2D array representing the fractal
        """
        iterations = params.get('iterations', self.iterations)
        return compute_barnsley_fern(width, height, bounds, iterations)
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get adjustable parameters."""
        params = super().get_parameters()
        params.update({
            'color_mode': {
                'type': str,
                'default': 'density',
                'options': ['density', 'height', 'age'],
                'description': 'Coloring mode for the fern'
            }
        })
        return params


@jit(nopython=True)
def compute_barnsley_fern(width: int, height: int, bounds: Tuple[float, float, float, float],
                          iterations: int) -> np.ndarray:
    """Optimized Barnsley Fern computation.
    
    Args:
        width: Width in pixels
        height: Height in pixels
        bounds: Coordinate bounds
        iterations: Number of iterations
        
    Returns:
        2D array of the fractal
    """
    xmin, xmax, ymin, ymax = bounds
    result = np.zeros((height, width), dtype=np.float32)
    
    # Starting point
    x, y = 0.0, 0.0
    
    # Probabilities for each transform
    probs = np.array([0.01, 0.86, 0.93, 1.0])  # Cumulative probabilities
    
    # Skip first iterations
    skip = min(100, iterations // 100)
    
    for i in range(iterations + skip):
        # Random choice based on probabilities
        r = np.random.random()
        
        if r < probs[0]:  # Transform 1 (1%)
            x, y = 0.0, 0.16 * y
        elif r < probs[1]:  # Transform 2 (85%)
            x, y = 0.85 * x + 0.04 * y, -0.04 * x + 0.85 * y + 1.6
        elif r < probs[2]:  # Transform 3 (7%)
            x, y = 0.2 * x - 0.26 * y, 0.23 * x + 0.22 * y + 1.6
        else:  # Transform 4 (7%)
            x, y = -0.15 * x + 0.28 * y, 0.26 * x + 0.24 * y + 0.44
        
        if i < skip:
            continue
            
        # Map to pixel coordinates with anti-aliasing
        fx = (x - xmin) / (xmax - xmin) * (width - 1)
        fy = (y - ymin) / (ymax - ymin) * (height - 1)
        
        px = int(fx)
        py = int(fy)
        
        # Apply anti-aliasing with bilinear interpolation
        if 0 <= px < width-1 and 0 <= py < height-1:
            dx = fx - px
            dy = fy - py
            w00 = (1 - dx) * (1 - dy)
            w10 = dx * (1 - dy)
            w01 = (1 - dx) * dy
            w11 = dx * dy
            
            result[height - 1 - py, px] += w00
            result[height - 1 - py, px + 1] += w10
            result[height - 1 - (py + 1), px] += w01
            result[height - 1 - (py + 1), px + 1] += w11
        elif 0 <= px < width and 0 <= py < height:
            result[height - 1 - py, px] += 1
    
    # Apply logarithmic scaling for better visualization
    if result.max() > 0:
        result = np.log1p(result)
        result = result / result.max()
        
    return result


class DragonCurve(IFSFractal):
    """Dragon Curve fractal using IFS."""
    
    def __init__(self):
        """Initialize Dragon Curve."""
        super().__init__("Dragon Curve", iterations=500000)
        
    def get_transforms(self) -> List[Tuple[Callable, float]]:
        """Get the transformation functions for Dragon Curve.
        
        Returns:
            List of (transform_function, probability) tuples
        """
        def transform1(x: float, y: float) -> Tuple[float, float]:
            return 0.5 * x - 0.5 * y, 0.5 * x + 0.5 * y
        
        def transform2(x: float, y: float) -> Tuple[float, float]:
            return -0.5 * x + 0.5 * y + 1, -0.5 * x - 0.5 * y
        
        return [
            (transform1, 0.5),
            (transform2, 0.5)
        ]
    
    def get_default_bounds(self) -> Tuple[float, float, float, float]:
        """Get default viewing bounds."""
        return (-0.5, 1.5, -0.75, 0.75)
    
    def compute(self, width: int, height: int, bounds: Tuple[float, float, float, float],
                **params) -> np.ndarray:
        """Compute Dragon Curve using optimized method.
        
        Args:
            width: Width in pixels
            height: Height in pixels
            bounds: (xmin, xmax, ymin, ymax) coordinate bounds
            **params: Additional parameters
            
        Returns:
            2D array representing the fractal
        """
        iterations = params.get('iterations', self.iterations)
        return compute_dragon_curve(width, height, bounds, iterations)


@jit(nopython=True)
def compute_dragon_curve(width: int, height: int, bounds: Tuple[float, float, float, float],
                         iterations: int) -> np.ndarray:
    """Optimized Dragon Curve computation.
    
    Args:
        width: Width in pixels
        height: Height in pixels
        bounds: Coordinate bounds
        iterations: Number of iterations
        
    Returns:
        2D array of the fractal
    """
    xmin, xmax, ymin, ymax = bounds
    result = np.zeros((height, width), dtype=np.float32)
    
    # Starting point
    x, y = 0.5, 0.0
    
    # Skip first iterations
    skip = min(100, iterations // 100)
    
    for i in range(iterations + skip):
        # Random choice between 2 transforms (equal probability)
        if np.random.random() < 0.5:
            x, y = 0.5 * x - 0.5 * y, 0.5 * x + 0.5 * y
        else:
            x, y = -0.5 * x + 0.5 * y + 1, -0.5 * x - 0.5 * y
        
        if i < skip:
            continue
            
        # Map to pixel coordinates with anti-aliasing
        fx = (x - xmin) / (xmax - xmin) * (width - 1)
        fy = (y - ymin) / (ymax - ymin) * (height - 1)
        
        px = int(fx)
        py = int(fy)
        
        # Apply anti-aliasing with bilinear interpolation
        if 0 <= px < width-1 and 0 <= py < height-1:
            dx = fx - px
            dy = fy - py
            w00 = (1 - dx) * (1 - dy)
            w10 = dx * (1 - dy)
            w01 = (1 - dx) * dy
            w11 = dx * dy
            
            result[height - 1 - py, px] += w00
            result[height - 1 - py, px + 1] += w10
            result[height - 1 - (py + 1), px] += w01
            result[height - 1 - (py + 1), px + 1] += w11
        elif 0 <= px < width and 0 <= py < height:
            result[height - 1 - py, px] += 1
    
    # Normalize
    if result.max() > 0:
        result = np.log1p(result)
        result = result / result.max()
        
    return result