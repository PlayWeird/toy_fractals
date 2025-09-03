#!/usr/bin/env python3
"""Specific test for Sierpinski Triangle zoom behavior."""

import sys
import os
import numpy as np

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_sierpinski_zoom_behavior():
    """Test that Sierpinski Triangle maintains structure when zoomed."""
    print("=" * 60)
    print("TESTING SIERPINSKI TRIANGLE ZOOM BEHAVIOR")
    print("=" * 60)
    
    try:
        from fractal_explorer.fractals import SierpinskiTriangle
        from fractal_explorer.rendering import FractalRenderer2D
        
        # Create fractal and renderer
        sierpinski = SierpinskiTriangle()
        renderer = FractalRenderer2D(sierpinski, 500, 500)
        
        print("Testing zoom behavior with different methods...")
        
        # Test scenarios: progressively deeper zooms
        zoom_tests = [
            ("Default view", sierpinski.get_default_bounds(), 1.0),
            ("2x zoom", (0.0, 0.6, 0.0, 0.55), 2.0),
            ("5x zoom", (0.2, 0.44, 0.2, 0.44), 5.0),
            ("10x zoom", (0.25, 0.35, 0.25, 0.35), 12.0),
        ]
        
        results = []
        
        for name, bounds, expected_zoom in zoom_tests:
            print(f"\n{name} (expected zoom: {expected_zoom:.1f}x):")
            
            # Test WITH improvements
            image_improved = renderer.render(bounds=bounds, progressive=False, 
                                           adaptive_iter=True)
            coverage_improved = np.count_nonzero(image_improved) / image_improved.size * 100
            
            # Test WITHOUT improvements (for comparison)
            base_iterations = sierpinski.iterations
            image_basic = renderer.render(bounds=bounds, progressive=False, 
                                        iterations=base_iterations, adaptive_iter=False)
            coverage_basic = np.count_nonzero(image_basic) / image_basic.size * 100
            
            # Calculate actual zoom level
            default_bounds = sierpinski.get_default_bounds()
            default_width = default_bounds[1] - default_bounds[0]
            current_width = bounds[1] - bounds[0]
            actual_zoom = default_width / current_width
            
            # Get adaptive iteration count
            adaptive_iter = sierpinski.adaptive_iterations_for_zoom(bounds, base_iterations)
            
            print(f"  Actual zoom: {actual_zoom:.1f}x")
            print(f"  Base iterations: {base_iterations:,}")
            print(f"  Adaptive iterations: {adaptive_iter:,} ({adaptive_iter/base_iterations:.1f}x)")
            print(f"  Coverage without improvements: {coverage_basic:.1f}%")
            print(f"  Coverage with improvements: {coverage_improved:.1f}%")
            
            improvement = coverage_improved - coverage_basic
            print(f"  Improvement: {improvement:+.1f}%")
            
            # Assess quality
            if coverage_improved > 25:  # Should maintain reasonable density
                quality = "Good"
            elif coverage_improved > 15:
                quality = "Fair"
            else:
                quality = "Poor"
            
            print(f"  Quality assessment: {quality}")
            
            results.append({
                'name': name,
                'zoom': actual_zoom,
                'coverage_basic': coverage_basic,
                'coverage_improved': coverage_improved,
                'improvement': improvement,
                'quality': quality
            })
        
        # Summary
        print("\n" + "=" * 60)
        print("ZOOM TEST SUMMARY")
        print("=" * 60)
        
        print(f"{'Zoom Level':<12} {'Basic':<8} {'Improved':<9} {'Gain':<6} {'Quality':<8}")
        print("-" * 50)
        
        for result in results:
            print(f"{result['zoom']:>8.1f}x   "
                  f"{result['coverage_basic']:>6.1f}%  "
                  f"{result['coverage_improved']:>7.1f}%  "
                  f"{result['improvement']:>+5.1f}%  "
                  f"{result['quality']:<8}")
        
        # Check if improvements are working
        avg_improvement = sum(r['improvement'] for r in results) / len(results)
        high_zoom_quality = results[-1]['quality']  # Quality at highest zoom
        
        print(f"\nAverage improvement: {avg_improvement:+.1f}%")
        print(f"Quality at 10x zoom: {high_zoom_quality}")
        
        if avg_improvement > 2 and high_zoom_quality in ['Good', 'Fair']:
            print("\n✓ Sierpinski Triangle zoom improvements are working!")
            print("  The fractal should maintain structure when zoomed in.")
        else:
            print("\n⚠ Zoom improvements may need further tuning.")
            print("  The fractal might still become sparse when zoomed.")
        
        return True
        
    except Exception as e:
        print(f"✗ Sierpinski zoom test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run the Sierpinski zoom test."""
    print("SIERPINSKI TRIANGLE - ZOOM BEHAVIOR TEST")
    
    success = test_sierpinski_zoom_behavior()
    
    if success:
        print("\n🎯 TEST COMPLETED")
        print("\nTo test manually:")
        print("1. Run: python -m fractal_explorer.main")
        print("2. Select 'Sierpinski Triangle'")
        print("3. Use Shift+drag to zoom into different areas")
        print("4. The fractal should maintain its triangular structure")
        print("5. Higher zoom levels should show more detail, not just sparse dots")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)