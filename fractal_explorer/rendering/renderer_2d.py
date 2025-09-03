"""2D fractal renderer with progressive rendering support."""

import numpy as np
from typing import Tuple, Optional, Callable
import time
from concurrent.futures import ThreadPoolExecutor
from ..fractals.base import Fractal
from .colormaps import ColorMapper


class FractalRenderer2D:
    """2D fractal renderer with progressive rendering and caching."""
    
    def __init__(self, fractal: Fractal, width: int = 800, height: int = 600):
        """Initialize the renderer.
        
        Args:
            fractal: Fractal instance to render
            width: Canvas width in pixels
            height: Canvas height in pixels
        """
        self.fractal = fractal
        self.width = width
        self.height = height
        self.color_mapper = ColorMapper()
        
        # Rendering state
        self.current_bounds = fractal.get_default_bounds()
        self.current_data = None
        self.render_time = 0.0
        
        # Progressive rendering settings
        self.progressive_levels = [8, 4, 2, 1]  # Downsampling factors
        self.current_level = 0
        
        # Cache for rendered regions
        self._cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
    def render(self, bounds: Optional[Tuple[float, float, float, float]] = None,
              progressive: bool = True, **params) -> np.ndarray:
        """Render the fractal.
        
        Args:
            bounds: (xmin, xmax, ymin, ymax) or None for current bounds
            progressive: Whether to use progressive rendering
            **params: Additional parameters for fractal computation
            
        Returns:
            RGB image array (height, width, 3)
        """
        if bounds is not None:
            self.current_bounds = bounds
            
        start_time = time.time()
        
        if progressive:
            image = self._progressive_render(self.current_bounds, **params)
        else:
            data = self.fractal.compute(self.width, self.height, 
                                       self.current_bounds, **params)
            self.current_data = data
            image = self.color_mapper.get_colors(data)
            
        self.render_time = time.time() - start_time
        return image
    
    def _progressive_render(self, bounds: Tuple[float, float, float, float],
                           **params) -> np.ndarray:
        """Perform progressive rendering from coarse to fine.
        
        Args:
            bounds: Coordinate bounds
            **params: Additional parameters
            
        Returns:
            RGB image array
        """
        final_image = None
        
        for level in self.progressive_levels:
            # Calculate reduced dimensions
            w = self.width // level
            h = self.height // level
            
            # Compute at reduced resolution
            data = self.fractal.compute(w, h, bounds, **params)
            
            # Upscale to full resolution
            if level > 1:
                data = self._upscale(data, self.width, self.height)
                
            self.current_data = data
            
            # Convert to colors
            final_image = self.color_mapper.get_colors(data)
            
            # For real-time display, you would yield here
            # yield final_image
            
        return final_image
    
    def _upscale(self, data: np.ndarray, target_width: int, 
                 target_height: int) -> np.ndarray:
        """Upscale data using bilinear interpolation.
        
        Args:
            data: Input data array
            target_width: Target width
            target_height: Target height
            
        Returns:
            Upscaled array
        """
        from scipy import ndimage
        
        h, w = data.shape
        scale_y = target_height / h
        scale_x = target_width / w
        
        return ndimage.zoom(data, (scale_y, scale_x), order=1)
    
    def zoom(self, center_x: float, center_y: float, zoom_factor: float):
        """Zoom in/out at a specific point.
        
        Args:
            center_x: X coordinate of zoom center (pixel)
            center_y: Y coordinate of zoom center (pixel)
            zoom_factor: Zoom factor (>1 to zoom in, <1 to zoom out)
        """
        xmin, xmax, ymin, ymax = self.current_bounds
        
        # Convert pixel to fractal coordinates
        fx = xmin + (center_x / self.width) * (xmax - xmin)
        fy = ymin + (center_y / self.height) * (ymax - ymin)
        
        # Calculate new bounds
        new_width = (xmax - xmin) / zoom_factor
        new_height = (ymax - ymin) / zoom_factor
        
        self.current_bounds = (
            fx - new_width / 2,
            fx + new_width / 2,
            fy - new_height / 2,
            fy + new_height / 2
        )
    
    def zoom_rectangle(self, x1: int, y1: int, x2: int, y2: int):
        """Zoom to a rectangular region.
        
        Args:
            x1, y1: Top-left corner (pixels)
            x2, y2: Bottom-right corner (pixels)
        """
        xmin, xmax, ymin, ymax = self.current_bounds
        
        # Convert pixels to fractal coordinates
        fx1 = xmin + (x1 / self.width) * (xmax - xmin)
        fx2 = xmin + (x2 / self.width) * (xmax - xmin)
        fy1 = ymin + (y1 / self.height) * (ymax - ymin)
        fy2 = ymin + (y2 / self.height) * (ymax - ymin)
        
        self.current_bounds = (
            min(fx1, fx2), max(fx1, fx2),
            min(fy1, fy2), max(fy1, fy2)
        )
    
    def pan(self, dx: int, dy: int):
        """Pan the view by pixel amounts.
        
        Args:
            dx: Horizontal displacement in pixels
            dy: Vertical displacement in pixels
        """
        xmin, xmax, ymin, ymax = self.current_bounds
        
        # Convert pixel displacement to fractal coordinates
        fx_delta = (dx / self.width) * (xmax - xmin)
        fy_delta = (dy / self.height) * (ymax - ymin)
        
        self.current_bounds = (
            xmin + fx_delta, xmax + fx_delta,
            ymin + fy_delta, ymax + fy_delta
        )
    
    def reset_view(self):
        """Reset to default viewing bounds."""
        self.current_bounds = self.fractal.get_default_bounds()
        self._cache.clear()
    
    def get_zoom_level(self) -> float:
        """Calculate current zoom level relative to default view.
        
        Returns:
            Zoom level (1.0 = default)
        """
        default_bounds = self.fractal.get_default_bounds()
        default_width = default_bounds[1] - default_bounds[0]
        current_width = self.current_bounds[1] - self.current_bounds[0]
        
        return default_width / current_width
    
    def get_center_coordinates(self) -> Tuple[float, float]:
        """Get the center coordinates of current view.
        
        Returns:
            (center_x, center_y) in fractal coordinates
        """
        xmin, xmax, ymin, ymax = self.current_bounds
        return ((xmin + xmax) / 2, (ymin + ymax) / 2)
    
    def pixel_to_fractal(self, px: int, py: int) -> Tuple[float, float]:
        """Convert pixel coordinates to fractal coordinates.
        
        Args:
            px: Pixel x coordinate
            py: Pixel y coordinate
            
        Returns:
            (fx, fy) fractal coordinates
        """
        xmin, xmax, ymin, ymax = self.current_bounds
        
        fx = xmin + (px / self.width) * (xmax - xmin)
        fy = ymin + (py / self.height) * (ymax - ymin)
        
        return (fx, fy)
    
    def save_image(self, filename: str, image: Optional[np.ndarray] = None,
                  high_res: bool = False):
        """Save the current or provided image to file.
        
        Args:
            filename: Output filename
            image: Image array or None to render current view
            high_res: Whether to render at higher resolution
        """
        from PIL import Image
        
        if image is None:
            if high_res:
                # Render at 2x resolution
                old_width, old_height = self.width, self.height
                self.width *= 2
                self.height *= 2
                image = self.render(progressive=False)
                self.width, self.height = old_width, old_height
            else:
                image = self.render(progressive=False)
                
        # Convert to uint8
        image_uint8 = (image * 255).astype(np.uint8)
        
        # Save using PIL
        img = Image.fromarray(image_uint8)
        img.save(filename)
    
    def get_stats(self) -> dict:
        """Get rendering statistics.
        
        Returns:
            Dictionary of statistics
        """
        return {
            'render_time': self.render_time,
            'zoom_level': self.get_zoom_level(),
            'center': self.get_center_coordinates(),
            'bounds': self.current_bounds,
            'resolution': (self.width, self.height),
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'fractal_type': self.fractal.get_type()
        }