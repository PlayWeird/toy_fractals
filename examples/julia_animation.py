"""Create an animation of Julia sets with varying c parameter."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from fractal_explorer.fractals import JuliaSet
from fractal_explorer.rendering import FractalRenderer2D


def create_julia_animation():
    """Create and save a Julia set animation."""
    
    print("Setting up Julia set animation...")
    
    # Create Julia set and renderer
    julia = JuliaSet()
    renderer = FractalRenderer2D(julia, width=600, height=600)
    renderer.color_mapper.palette = 'twilight'
    
    # Setup the figure
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.axis('off')
    
    # Initial image
    image = renderer.render(progressive=False)
    im = ax.imshow(image)
    
    # Animation parameters
    n_frames = 100
    
    def animate(frame):
        """Update function for animation."""
        # Calculate c parameter based on frame
        t = 2 * np.pi * frame / n_frames
        
        # Circular path in complex plane
        c_real = 0.7885 * np.cos(t)
        c_imag = 0.7885 * np.sin(t)
        
        # Render with new parameters
        image = renderer.render(
            progressive=False,
            c_real=c_real,
            c_imag=c_imag,
            max_iter=256
        )
        
        im.set_array(image)
        ax.set_title(f"Julia Set: c = {c_real:.3f} + {c_imag:.3f}i")
        
        if frame % 10 == 0:
            print(f"Frame {frame}/{n_frames} rendered")
        
        return [im]
    
    # Create animation
    print("Creating animation (this may take a while)...")
    anim = FuncAnimation(fig, animate, frames=n_frames, 
                        interval=50, blit=True, repeat=True)
    
    # Save as GIF (requires pillow or imagemagick)
    output_file = "julia_animation.gif"
    print(f"Saving animation to {output_file}...")
    anim.save(output_file, writer='pillow', fps=20)
    print(f"Animation saved to {output_file}")
    
    # Show the animation
    plt.show()


def explore_julia_constants():
    """Explore different Julia set constants."""
    
    print("\nExploring interesting Julia set constants...")
    
    julia = JuliaSet()
    renderer = FractalRenderer2D(julia, width=400, height=400)
    
    # Get interesting constants
    constants = julia.get_interesting_constants()
    
    # Create subplot grid
    n_constants = len(constants)
    cols = 3
    rows = (n_constants + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(12, 4*rows))
    if rows == 1:
        axes = axes.reshape(1, -1)
    
    fig.suptitle("Julia Set Gallery - Interesting Constants", fontsize=16)
    
    for idx, (name, (c_real, c_imag)) in enumerate(constants.items()):
        row = idx // cols
        col = idx % cols
        ax = axes[row, col]
        
        print(f"Rendering {name} Julia set...")
        
        # Use different palette for each
        palettes = ['classic', 'fire', 'ocean', 'twilight', 'rainbow']
        renderer.color_mapper.palette = palettes[idx % len(palettes)]
        
        image = renderer.render(
            progressive=False,
            c_real=c_real,
            c_imag=c_imag,
            max_iter=256
        )
        
        ax.imshow(image)
        ax.set_title(f"{name}\nc = {c_real:.3f} + {c_imag:.3f}i")
        ax.axis('off')
    
    # Hide unused subplots
    for idx in range(n_constants, rows * cols):
        row = idx // cols
        col = idx % cols
        axes[row, col].axis('off')
    
    plt.tight_layout()
    
    # Save the gallery
    output_file = "julia_gallery.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nGallery saved to {output_file}")
    
    plt.show()


if __name__ == "__main__":
    # Create animation
    create_julia_animation()
    
    # Explore different constants
    explore_julia_constants()