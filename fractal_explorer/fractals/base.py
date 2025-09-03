"""Base classes for all fractal implementations."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
import numpy as np


class Fractal(ABC):
    """Abstract base class for all fractal types."""
    
    def __init__(self, name: str):
        """Initialize fractal with a name.
        
        Args:
            name: Human-readable name for the fractal
        """
        self.name = name
        self._cache = {}
        
    @abstractmethod
    def compute(self, width: int, height: int, bounds: Tuple[float, float, float, float], 
                **params) -> np.ndarray:
        """Compute the fractal for given dimensions and bounds.
        
        Args:
            width: Width in pixels
            height: Height in pixels
            bounds: (xmin, xmax, ymin, ymax) coordinate bounds
            **params: Additional parameters specific to the fractal
            
        Returns:
            2D array of computed values
        """
        pass
    
    @abstractmethod
    def get_default_bounds(self) -> Tuple[float, float, float, float]:
        """Get default viewing bounds for this fractal.
        
        Returns:
            Tuple of (xmin, xmax, ymin, ymax)
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Get adjustable parameters for this fractal.
        
        Returns:
            Dictionary mapping parameter names to their properties:
            {
                'param_name': {
                    'type': type,
                    'default': default_value,
                    'min': min_value (optional),
                    'max': max_value (optional),
                    'step': step_size (optional),
                    'description': str
                }
            }
        """
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        """Get the fractal type category.
        
        Returns:
            String indicating type: 'escape_time', 'ifs', 'lsystem', etc.
        """
        pass
    
    def clear_cache(self):
        """Clear any cached computations."""
        self._cache.clear()


class EscapeTimeFractal(Fractal):
    """Base class for escape-time fractals like Mandelbrot and Julia sets."""
    
    def __init__(self, name: str, max_iter: int = 256):
        """Initialize escape-time fractal.
        
        Args:
            name: Human-readable name
            max_iter: Maximum iterations for escape calculation
        """
        super().__init__(name)
        self.max_iter = max_iter
        
    def get_type(self) -> str:
        """Return fractal type."""
        return 'escape_time'
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get base parameters for escape-time fractals."""
        return {
            'max_iter': {
                'type': int,
                'default': 256,
                'min': 10,
                'max': 2000,
                'step': 10,
                'description': 'Maximum iterations for escape calculation'
            }
        }
    
    def adaptive_iterations(self, zoom_level: float) -> int:
        """Calculate adaptive iteration count based on zoom level.
        
        Args:
            zoom_level: Current zoom factor
            
        Returns:
            Adjusted maximum iterations
        """
        base_iter = self.max_iter
        return min(int(base_iter * (1 + np.log10(max(1, zoom_level)))), 2000)
    
    @abstractmethod
    def escape_calculation(self, c: np.ndarray, max_iter: int) -> np.ndarray:
        """Perform the escape-time calculation for given complex points.
        
        Args:
            c: Array of complex numbers
            max_iter: Maximum iterations
            
        Returns:
            Array of iteration counts
        """
        pass


class IFSFractal(Fractal):
    """Base class for Iterated Function System fractals."""
    
    def __init__(self, name: str, iterations: int = 100000):
        """Initialize IFS fractal.
        
        Args:
            name: Human-readable name
            iterations: Number of iterations for IFS
        """
        super().__init__(name)
        self.iterations = iterations
        
    def get_type(self) -> str:
        """Return fractal type."""
        return 'ifs'
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get base parameters for IFS fractals."""
        return {
            'iterations': {
                'type': int,
                'default': self.iterations,
                'min': 10000,
                'max': 5000000,
                'step': 50000,
                'description': 'IFS Iterations'
            }
        }
    
    @abstractmethod
    def get_transforms(self) -> list:
        """Get the transformation functions and their probabilities.
        
        Returns:
            List of (transform_function, probability) tuples
        """
        pass
    
    def adaptive_iterations_for_zoom(self, bounds: Tuple[float, float, float, float], 
                                   base_iterations: int) -> int:
        """Calculate adaptive iteration count based on zoom level.
        
        Args:
            bounds: Current viewing bounds
            base_iterations: Base number of iterations
            
        Returns:
            Adjusted iteration count
        """
        # Get default bounds to calculate zoom level
        default_bounds = self.get_default_bounds()
        default_width = default_bounds[1] - default_bounds[0]
        current_width = bounds[1] - bounds[0]
        
        # Calculate zoom level (higher = more zoomed in)
        zoom_level = default_width / current_width
        
        # Scale iterations based on zoom level
        # Use square root to avoid excessive iteration counts
        zoom_factor = max(1.0, zoom_level ** 0.75)
        
        # Cap the maximum iterations to prevent excessive computation
        max_iterations = min(base_iterations * 10, 10000000)
        adjusted_iterations = int(base_iterations * zoom_factor)
        
        return min(adjusted_iterations, max_iterations)
    
    def compute(self, width: int, height: int, bounds: Tuple[float, float, float, float],
                **params) -> np.ndarray:
        """Compute IFS fractal using random iteration algorithm.
        
        Args:
            width: Width in pixels
            height: Height in pixels
            bounds: (xmin, xmax, ymin, ymax) coordinate bounds
            **params: Additional parameters
            
        Returns:
            2D array representing the fractal
        """
        iterations = params.get('iterations', self.iterations)
        xmin, xmax, ymin, ymax = bounds
        
        # Apply adaptive iteration scaling based on zoom level
        if params.get('adaptive_iter', True):
            iterations = self.adaptive_iterations_for_zoom(bounds, iterations)
        
        # Initialize result array
        result = np.zeros((height, width), dtype=np.float32)
        
        # Get transforms and probabilities
        transforms = self.get_transforms()
        probabilities = np.array([p for _, p in transforms])
        probabilities = probabilities / probabilities.sum()
        
        # Starting point
        x, y = 0.0, 0.0
        
        # Skip first iterations to let the point settle
        skip = min(100, iterations // 100)
        
        for i in range(iterations + skip):
            # Choose random transform based on probabilities
            choice = np.random.choice(len(transforms), p=probabilities)
            transform_func, _ = transforms[choice]
            
            # Apply transform
            x, y = transform_func(x, y)
            
            if i < skip:
                continue
                
            # Map to pixel coordinates with sub-pixel accuracy
            fx = (x - xmin) / (xmax - xmin) * (width - 1)
            fy = (y - ymin) / (ymax - ymin) * (height - 1)
            
            px = int(fx)
            py = int(fy)
            
            # Apply anti-aliasing by distributing the point across nearby pixels
            if 0 <= px < width-1 and 0 <= py < height-1:
                # Calculate fractional parts for anti-aliasing
                dx = fx - px
                dy = fy - py
                
                # Distribute the point weight across 4 neighboring pixels (bilinear)
                w00 = (1 - dx) * (1 - dy)
                w10 = dx * (1 - dy) 
                w01 = (1 - dx) * dy
                w11 = dx * dy
                
                result[height - 1 - py, px] += w00
                result[height - 1 - py, px + 1] += w10
                result[height - 1 - (py + 1), px] += w01
                result[height - 1 - (py + 1), px + 1] += w11
            elif 0 <= px < width and 0 <= py < height:
                # Fall back to single pixel for edge cases
                result[height - 1 - py, px] += 1
                
        # Normalize and apply logarithmic scaling for better visualization
        result = np.where(result > 0, np.log1p(result), 0)
        if result.max() > 0:
            result = result / result.max()
            
        return result


class LSystemFractal(Fractal):
    """Base class for L-System fractals."""
    
    def __init__(self, name: str, iterations: int = 5):
        """Initialize L-System fractal.
        
        Args:
            name: Human-readable name
            iterations: Number of iterations for L-System
        """
        super().__init__(name)
        self.iterations = iterations
        
    def get_type(self) -> str:
        """Return fractal type."""
        return 'lsystem'
    
    @abstractmethod
    def get_rules(self) -> Dict[str, str]:
        """Get the L-System production rules.
        
        Returns:
            Dictionary mapping symbols to their replacements
        """
        pass
    
    @abstractmethod
    def get_axiom(self) -> str:
        """Get the starting axiom for the L-System.
        
        Returns:
            Initial string
        """
        pass