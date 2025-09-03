"""Quick test script to verify the fractal explorer installation."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        # Core modules
        from fractal_explorer import FractalExplorer
        print("✓ Main app module")
        
        # Fractals
        from fractal_explorer.fractals import (
            MandelbrotSet, JuliaSet, BurningShip,
            SierpinskiTriangle, BarnsleyFern
        )
        print("✓ Fractal implementations")
        
        # Rendering
        from fractal_explorer.rendering import FractalRenderer2D, ColorMapper
        print("✓ Rendering modules")
        
        # UI (PyQt5)
        from fractal_explorer.ui import FractalExplorerWindow
        print("✓ UI components")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_fractal_computation():
    """Test basic fractal computation."""
    print("\nTesting fractal computation...")
    
    try:
        from fractal_explorer.fractals import MandelbrotSet
        import numpy as np
        
        # Create and compute a small Mandelbrot set
        fractal = MandelbrotSet()
        bounds = fractal.get_default_bounds()
        data = fractal.compute(100, 100, bounds, max_iter=50)
        
        # Check output
        assert isinstance(data, np.ndarray)
        assert data.shape == (100, 100)
        assert data.min() >= 0
        
        print(f"✓ Mandelbrot computation: shape={data.shape}, min={data.min():.2f}, max={data.max():.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Computation error: {e}")
        return False


def test_renderer():
    """Test the renderer."""
    print("\nTesting renderer...")
    
    try:
        from fractal_explorer.fractals import JuliaSet
        from fractal_explorer.rendering import FractalRenderer2D
        
        # Create renderer
        fractal = JuliaSet()
        renderer = FractalRenderer2D(fractal, width=200, height=200)
        
        # Render
        image = renderer.render(progressive=False, max_iter=50)
        
        # Check output
        assert image.shape == (200, 200, 3)
        assert image.min() >= 0
        assert image.max() <= 1
        
        print(f"✓ Renderer: shape={image.shape}, render_time={renderer.render_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"✗ Renderer error: {e}")
        return False


def test_color_palettes():
    """Test color palette functionality."""
    print("\nTesting color palettes...")
    
    try:
        from fractal_explorer.rendering.colormaps import ColorMapper, get_available_palettes
        import numpy as np
        
        # Get available palettes
        palettes = get_available_palettes()
        print(f"✓ Found {len(palettes)} color palettes: {', '.join(list(palettes.keys())[:5])}...")
        
        # Test color mapping
        mapper = ColorMapper(palette='fire')
        test_data = np.random.rand(50, 50)
        colors = mapper.get_colors(test_data)
        
        assert colors.shape == (50, 50, 3)
        assert colors.min() >= 0
        assert colors.max() <= 1
        
        print(f"✓ Color mapping works correctly")
        
        return True
        
    except Exception as e:
        print(f"✗ Color palette error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Fractal Explorer Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_fractal_computation,
        test_renderer,
        test_color_palettes
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All {total} tests passed!")
        print("\nYou can now run the application with:")
        print("  python -m fractal_explorer.main")
        print("\nOr try the examples:")
        print("  python examples/basic_mandelbrot.py")
        print("  python examples/julia_animation.py")
    else:
        print(f"✗ {passed}/{total} tests passed")
        print("Please check the error messages above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)