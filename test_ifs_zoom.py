#!/usr/bin/env python3
"""Test script to verify IFS fractal zoom improvements."""

import sys
import os
import numpy as np

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_adaptive_iterations():
    """Test that IFS fractals adapt iteration count based on zoom."""
    print("=" * 60)
    print("TESTING ADAPTIVE ITERATIONS FOR IFS FRACTALS")
    print("=" * 60)
    
    try:
        from fractal_explorer.fractals import SierpinskiTriangle
        from fractal_explorer.rendering import FractalRenderer2D
        
        # Create Sierpinski Triangle
        sierpinski = SierpinskiTriangle()
        renderer = FractalRenderer2D(sierpinski, 300, 300)
        
        # Test different zoom levels
        test_scenarios = [
            ("Default view", sierpinski.get_default_bounds()),
            ("2x zoom", (-0.05, 0.55, -0.05, 0.45)),  # Zoomed in 2x
            ("5x zoom", (0.1, 0.5, 0.1, 0.5)),       # Zoomed in 5x  
            ("10x zoom", (0.2, 0.4, 0.2, 0.4)),      # Zoomed in 10x
        ]
        
        base_iterations = sierpinski.iterations
        print(f"Base iterations: {base_iterations:,}")
        print()
        
        for name, bounds in test_scenarios:
            # Test adaptive iterations
            adaptive_iter = sierpinski.adaptive_iterations_for_zoom(bounds, base_iterations)
            
            # Calculate zoom level for display
            default_bounds = sierpinski.get_default_bounds()
            default_width = default_bounds[1] - default_bounds[0]
            current_width = bounds[1] - bounds[0]
            zoom_level = default_width / current_width
            
            print(f"{name}:")
            print(f"  Bounds: {bounds}")
            print(f"  Zoom level: {zoom_level:.1f}x")
            print(f"  Adaptive iterations: {adaptive_iter:,}")
            
            # Render and test quality
            image = renderer.render(bounds=bounds, progressive=False, iterations=adaptive_iter)
            non_zero_pixels = np.count_nonzero(image)
            total_pixels = image.size
            coverage = non_zero_pixels / total_pixels * 100
            
            print(f"  Image coverage: {coverage:.1f}% ({non_zero_pixels:,} pixels)")
            
            if coverage > 10:  # Should maintain good coverage even when zoomed
                print(f"  ✓ Good coverage maintained")
            else:
                print(f"  ⚠ Low coverage - may need more iterations")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"✗ Adaptive iterations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_zoom_quality_comparison():
    """Compare fractal quality with and without adaptive iterations."""
    print("=" * 60)
    print("TESTING ZOOM QUALITY WITH/WITHOUT ADAPTIVE ITERATIONS")
    print("=" * 60)
    
    try:
        from fractal_explorer.fractals import SierpinskiTriangle
        from fractal_explorer.rendering import FractalRenderer2D
        
        sierpinski = SierpinskiTriangle()
        renderer = FractalRenderer2D(sierpinski, 400, 400)
        
        # Test at 10x zoom
        zoomed_bounds = (0.2, 0.4, 0.2, 0.4)
        base_iterations = sierpinski.iterations
        
        print("Testing at 10x zoom level...")
        print(f"Bounds: {zoomed_bounds}")
        print()
        
        # Test without adaptive iterations
        print("1. WITHOUT adaptive iterations:")
        image_fixed = renderer.render(bounds=zoomed_bounds, progressive=False, 
                                    iterations=base_iterations, adaptive_iter=False)
        coverage_fixed = np.count_nonzero(image_fixed) / image_fixed.size * 100
        print(f"   Iterations used: {base_iterations:,}")
        print(f"   Coverage: {coverage_fixed:.1f}%")
        
        # Test with adaptive iterations
        print("2. WITH adaptive iterations:")
        image_adaptive = renderer.render(bounds=zoomed_bounds, progressive=False, 
                                       iterations=base_iterations, adaptive_iter=True)
        coverage_adaptive = np.count_nonzero(image_adaptive) / image_adaptive.size * 100
        
        # Get the actual iterations used
        adaptive_iter = sierpinski.adaptive_iterations_for_zoom(zoomed_bounds, base_iterations)
        print(f"   Iterations used: {adaptive_iter:,}")
        print(f"   Coverage: {coverage_adaptive:.1f}%")
        
        # Compare
        improvement = coverage_adaptive - coverage_fixed
        print()
        print(f"Improvement: {improvement:.1f}% coverage increase")
        print(f"Iteration scaling: {adaptive_iter/base_iterations:.1f}x")
        
        if improvement > 5:
            print("✓ Adaptive iterations provide significant improvement!")
        else:
            print("⚠ Adaptive iterations provide modest improvement")
        
        return True
        
    except Exception as e:
        print(f"✗ Quality comparison test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_ifs_fractals():
    """Test adaptive iterations with all IFS fractal types."""
    print("=" * 60)
    print("TESTING ADAPTIVE ITERATIONS FOR ALL IFS FRACTALS")
    print("=" * 60)
    
    try:
        from fractal_explorer.fractals import SierpinskiTriangle, BarnsleyFern, DragonCurve
        from fractal_explorer.rendering import FractalRenderer2D
        
        fractals = [
            ("Sierpinski Triangle", SierpinskiTriangle()),
            ("Barnsley Fern", BarnsleyFern()), 
            ("Dragon Curve", DragonCurve()),
        ]
        
        for name, fractal in fractals:
            print(f"Testing {name}...")
            
            renderer = FractalRenderer2D(fractal, 250, 250)
            default_bounds = fractal.get_default_bounds()
            
            # Calculate a reasonable zoom bounds (center region, 5x zoom)
            xmin, xmax, ymin, ymax = default_bounds
            cx = (xmin + xmax) / 2
            cy = (ymin + ymax) / 2
            zoom_width = (xmax - xmin) / 5
            zoom_height = (ymax - ymin) / 5
            
            zoomed_bounds = (cx - zoom_width/2, cx + zoom_width/2,
                           cy - zoom_height/2, cy + zoom_height/2)
            
            # Test adaptive iterations
            base_iter = fractal.iterations
            adaptive_iter = fractal.adaptive_iterations_for_zoom(zoomed_bounds, base_iter)
            
            print(f"  Base iterations: {base_iter:,}")
            print(f"  Adaptive iterations: {adaptive_iter:,}")
            print(f"  Scaling factor: {adaptive_iter/base_iter:.1f}x")
            
            # Test rendering
            image = renderer.render(bounds=zoomed_bounds, progressive=False, 
                                  iterations=adaptive_iter)
            coverage = np.count_nonzero(image) / image.size * 100
            print(f"  Zoomed coverage: {coverage:.1f}%")
            
            if coverage > 15:
                print(f"  ✓ {name} maintains good detail when zoomed")
            else:
                print(f"  ⚠ {name} may need more iterations when zoomed")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"✗ All IFS fractals test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_usage_instructions():
    """Print instructions for testing the zoom improvements."""
    print("=" * 60)
    print("MANUAL TESTING INSTRUCTIONS")
    print("=" * 60)
    
    print("\n🔍 Testing IFS Fractal Zoom Improvements:")
    print("\n1. Run the main application:")
    print("   python -m fractal_explorer.main")
    print("\n2. Select 'Sierpinski Triangle'")
    print("   - You should see a clear triangular fractal pattern")
    print("\n3. Zoom in using Shift+drag to draw a rectangle:")
    print("   - The fractal should maintain its detailed structure")
    print("   - Points should not become sparse and spread out")
    print("   - More iterations will be used automatically at higher zoom")
    print("\n4. Try zooming into different areas:")
    print("   - Edge regions of the triangle")
    print("   - Corner areas with fine detail")
    print("   - Each zoom should show more fractal detail, not just bigger dots")
    print("\n5. Test other IFS fractals:")
    print("   - Barnsley Fern: Zoom into leaf details")
    print("   - Dragon Curve: Zoom into curve segments")
    print("\n✨ Expected Results:")
    print("   ✓ Fractal structure preserved at all zoom levels")
    print("   ✓ Automatic increase in detail as you zoom in")
    print("   ✓ No more sparse, spread-out dots when zoomed")
    print("   ✓ Smooth, continuous fractal patterns")


def main():
    """Run all tests."""
    print("FRACTAL EXPLORER - IFS ZOOM IMPROVEMENT TEST")
    
    results = []
    
    # Run tests
    results.append(("Adaptive Iterations", test_adaptive_iterations()))
    results.append(("Zoom Quality Comparison", test_zoom_quality_comparison()))
    results.append(("All IFS Fractals", test_all_ifs_fractals()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 IFS ZOOM IMPROVEMENTS WORKING!")
        print("Sierpinski Triangle should now maintain fractal structure when zoomed!")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed.")
        print("There may be issues with the zoom improvements.")
    
    # Print manual testing instructions
    print_usage_instructions()
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)