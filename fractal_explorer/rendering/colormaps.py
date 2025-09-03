"""Color palette management for fractal rendering."""

import numpy as np
from typing import Tuple, List, Optional
import colorcet as cc


class ColorMapper:
    """Manages color mapping for fractal visualization."""
    
    # Predefined color palettes
    PALETTES = {
        'classic': {
            'name': 'Classic',
            'description': 'Traditional blue-white-orange fractal colors',
            'type': 'custom'
        },
        'fire': {
            'name': 'Fire',
            'description': 'Black to red to yellow to white',
            'type': 'custom'
        },
        'ocean': {
            'name': 'Ocean',
            'description': 'Deep blue to cyan to white',
            'type': 'custom'
        },
        'twilight': {
            'name': 'Twilight',
            'description': 'Purple to pink to orange sunset colors',
            'type': 'custom'
        },
        'rainbow': {
            'name': 'Rainbow',
            'description': 'Full spectrum rainbow colors',
            'type': 'custom'
        },
        'monochrome': {
            'name': 'Monochrome',
            'description': 'Black to white grayscale',
            'type': 'custom'
        },
        'coolwarm': {
            'name': 'Cool-Warm',
            'description': 'Blue to red diverging',
            'type': 'colorcet',
            'cmap': cc.coolwarm
        },
        'fire_colorcet': {
            'name': 'Fire (Colorcet)',
            'description': 'High quality fire colors',
            'type': 'colorcet',
            'cmap': cc.fire
        },
        'isolum': {
            'name': 'Isoluminant',
            'description': 'Perceptually uniform rainbow',
            'type': 'colorcet',
            'cmap': cc.isolum
        }
    }
    
    def __init__(self, palette: str = 'classic', invert: bool = False):
        """Initialize color mapper.
        
        Args:
            palette: Name of the color palette to use
            invert: Whether to invert the color palette
        """
        self.palette = palette
        self.invert = invert
        self._cache = {}
        
    def get_colors(self, values: np.ndarray, 
                   normalize: bool = True) -> np.ndarray:
        """Map fractal values to RGB colors.
        
        Args:
            values: 2D array of fractal values
            normalize: Whether to normalize values to [0, 1]
            
        Returns:
            3D array of RGB values (height, width, 3)
        """
        if normalize and values.max() > values.min():
            # Normalize to [0, 1]
            values = (values - values.min()) / (values.max() - values.min())
        
        if self.invert:
            values = 1.0 - values
            
        # Get the color mapping function
        if self.palette in self.PALETTES:
            palette_info = self.PALETTES[self.palette]
            
            if palette_info['type'] == 'custom':
                colors = self._get_custom_palette(self.palette, values)
            else:  # colorcet
                colors = self._apply_colorcet(palette_info['cmap'], values)
        else:
            # Default to classic if palette not found
            colors = self._get_custom_palette('classic', values)
            
        return colors
    
    def _get_custom_palette(self, name: str, values: np.ndarray) -> np.ndarray:
        """Get custom color palette.
        
        Args:
            name: Palette name
            values: Normalized values [0, 1]
            
        Returns:
            RGB color array
        """
        h, w = values.shape
        colors = np.zeros((h, w, 3), dtype=np.float32)
        
        if name == 'classic':
            # Classic fractal coloring
            colors[:, :, 0] = np.sin(values * np.pi) ** 2  # Red
            colors[:, :, 1] = np.sin(values * np.pi * 2) ** 2  # Green
            colors[:, :, 2] = np.cos(values * np.pi / 2) ** 2  # Blue
            
        elif name == 'fire':
            # Fire palette: black -> red -> yellow -> white
            colors[:, :, 0] = np.clip(values * 3, 0, 1)  # Red
            colors[:, :, 1] = np.clip(values * 3 - 1, 0, 1)  # Green
            colors[:, :, 2] = np.clip(values * 3 - 2, 0, 1)  # Blue
            
        elif name == 'ocean':
            # Ocean palette: dark blue -> cyan -> white
            colors[:, :, 0] = values ** 2  # Red
            colors[:, :, 1] = values ** 1.5  # Green
            colors[:, :, 2] = np.sqrt(values)  # Blue
            
        elif name == 'twilight':
            # Twilight: purple -> pink -> orange
            t = values
            colors[:, :, 0] = 0.5 + 0.5 * np.sin(2 * np.pi * t + 0)  # Red
            colors[:, :, 1] = 0.5 + 0.5 * np.sin(2 * np.pi * t - np.pi/2)  # Green
            colors[:, :, 2] = 0.5 + 0.5 * np.sin(2 * np.pi * t + np.pi/2)  # Blue
            
        elif name == 'rainbow':
            # HSV rainbow
            hue = values
            colors = self._hsv_to_rgb(hue, np.ones_like(values), np.ones_like(values))
            
        elif name == 'monochrome':
            # Grayscale
            colors[:, :, 0] = values
            colors[:, :, 1] = values
            colors[:, :, 2] = values
            
        return np.clip(colors, 0, 1)
    
    def _apply_colorcet(self, cmap: List, values: np.ndarray) -> np.ndarray:
        """Apply a colorcet colormap.
        
        Args:
            cmap: Colorcet colormap (list of hex colors)
            values: Normalized values [0, 1]
            
        Returns:
            RGB color array
        """
        # Convert hex colors to RGB
        rgb_colors = []
        for hex_color in cmap:
            rgb = tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (1, 3, 5))
            rgb_colors.append(rgb)
        
        rgb_array = np.array(rgb_colors)
        
        # Interpolate colors based on values
        h, w = values.shape
        colors = np.zeros((h, w, 3), dtype=np.float32)
        
        # Map values to indices in the colormap
        indices = values * (len(rgb_array) - 1)
        lower_idx = np.floor(indices).astype(int)
        upper_idx = np.ceil(indices).astype(int)
        fraction = indices - lower_idx
        
        # Clip indices
        lower_idx = np.clip(lower_idx, 0, len(rgb_array) - 1)
        upper_idx = np.clip(upper_idx, 0, len(rgb_array) - 1)
        
        # Interpolate between colors
        for i in range(3):
            colors[:, :, i] = (rgb_array[lower_idx, i] * (1 - fraction) +
                              rgb_array[upper_idx, i] * fraction)
        
        return colors
    
    def _hsv_to_rgb(self, h: np.ndarray, s: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Convert HSV to RGB.
        
        Args:
            h: Hue (0-1)
            s: Saturation (0-1)
            v: Value (0-1)
            
        Returns:
            RGB array
        """
        h = h * 6.0
        i = np.floor(h).astype(int)
        f = h - i
        
        p = v * (1 - s)
        q = v * (1 - s * f)
        t = v * (1 - s * (1 - f))
        
        i = i % 6
        
        rgb = np.zeros((*h.shape, 3), dtype=np.float32)
        
        # Each case for the 6 sectors of the color wheel
        mask = (i == 0)
        rgb[mask] = np.stack([v[mask], t[mask], p[mask]], axis=-1)
        
        mask = (i == 1)
        rgb[mask] = np.stack([q[mask], v[mask], p[mask]], axis=-1)
        
        mask = (i == 2)
        rgb[mask] = np.stack([p[mask], v[mask], t[mask]], axis=-1)
        
        mask = (i == 3)
        rgb[mask] = np.stack([p[mask], q[mask], v[mask]], axis=-1)
        
        mask = (i == 4)
        rgb[mask] = np.stack([t[mask], p[mask], v[mask]], axis=-1)
        
        mask = (i == 5)
        rgb[mask] = np.stack([v[mask], p[mask], q[mask]], axis=-1)
        
        return rgb
    
    def cycle_palette(self, forward: bool = True):
        """Cycle through available palettes.
        
        Args:
            forward: Direction to cycle (forward or backward)
        """
        palettes = list(self.PALETTES.keys())
        current_idx = palettes.index(self.palette)
        
        if forward:
            new_idx = (current_idx + 1) % len(palettes)
        else:
            new_idx = (current_idx - 1) % len(palettes)
            
        self.palette = palettes[new_idx]
        self._cache.clear()


def get_available_palettes() -> dict:
    """Get dictionary of available color palettes.
    
    Returns:
        Dictionary of palette information
    """
    return ColorMapper.PALETTES.copy()


def create_smooth_gradient(colors: List[Tuple[float, float, float]], 
                          steps: int = 256) -> np.ndarray:
    """Create a smooth gradient from a list of colors.
    
    Args:
        colors: List of RGB tuples (0-1 range)
        steps: Number of steps in the gradient
        
    Returns:
        Array of RGB values
    """
    gradient = np.zeros((steps, 3), dtype=np.float32)
    n_colors = len(colors)
    
    if n_colors == 1:
        gradient[:] = colors[0]
        return gradient
    
    segment_length = steps // (n_colors - 1)
    remainder = steps % (n_colors - 1)
    
    current_pos = 0
    for i in range(n_colors - 1):
        start_color = np.array(colors[i])
        end_color = np.array(colors[i + 1])
        
        # Add extra step to some segments to handle remainder
        seg_len = segment_length + (1 if i < remainder else 0)
        
        # Create linear interpolation
        for j in range(seg_len):
            t = j / (seg_len - 1) if seg_len > 1 else 0
            gradient[current_pos] = start_color * (1 - t) + end_color * t
            current_pos += 1
            
            if current_pos >= steps:
                break
                
    return gradient