"""Basic example of rendering the Mandelbrot set."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fractal_explorer.fractals import MandelbrotSet
from fractal_explorer.rendering import FractalRenderer2D, ColorMapper
import matplotlib.pyplot as plt


def main():
    """Render and display the Mandelbrot set."""
    
    print("Creating Mandelbrot set fractal...")
    fractal = MandelbrotSet()
    
    print("Setting up renderer...")
    renderer = FractalRenderer2D(fractal, width=800, height=600)
    
    # Render at default view
    print("Rendering default view...")
    image = renderer.render(progressive=False)
    
    # Display with matplotlib
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle("Mandelbrot Set - Different Views and Color Palettes")
    
    # Different interesting points
    views = [
        ("Default View", fractal.get_default_bounds()),
        ("Seahorse Valley", (-0.75, -0.735, 0.095, 0.105)),
        ("Elephant Valley", (0.270, 0.280, -0.005, 0.005)),
        ("Triple Spiral", (-0.090, -0.086, 0.652, 0.656)),
        ("Mini Mandelbrot", (-1.26, -1.24, -0.01, 0.01)),
        ("Dendrite Fractal", (-0.7454, -0.7451, 0.1130, 0.1133)),
    ]
    
    palettes = ['classic', 'fire', 'ocean', 'twilight', 'rainbow', 'monochrome']
    
    for idx, ((title, bounds), palette) in enumerate(zip(views, palettes)):
        row = idx // 3
        col = idx % 3
        ax = axes[row, col]
        
        print(f"Rendering {title} with {palette} palette...")
        renderer.color_mapper.palette = palette
        image = renderer.render(bounds=bounds, progressive=False, max_iter=512)
        
        ax.imshow(image)
        ax.set_title(f"{title}\n({palette} palette)")
        ax.axis('off')
        
        # Print statistics
        stats = renderer.get_stats()
        print(f"  - Zoom level: {stats['zoom_level']:.2f}x")
        print(f"  - Render time: {stats['render_time']:.3f}s")
    
    plt.tight_layout()
    
    # Save the figure
    output_file = "mandelbrot_gallery.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\nGallery saved to {output_file}")
    
    plt.show()
    
    # Interactive exploration
    print("\nFor interactive exploration, run: python -m fractal_explorer.main")


if __name__ == "__main__":
    main()