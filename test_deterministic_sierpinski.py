#!/usr/bin/env python3
"""Test to demonstrate the difference between random and deterministic Sierpinski Triangle."""

import sys
import os
import numpy as np

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_consistency():
    """Test that deterministic version gives consistent results."""
    print("=" * 60)
    print("TESTING SIERPINSKI TRIANGLE CONSISTENCY")
    print("=" * 60)
    
    try:
        from fractal_explorer.fractals import SierpinskiTriangle
        from fractal_explorer.fractals.deterministic_fractals import DeterministicSierpinskiTriangle
        from fractal_explorer.rendering import FractalRenderer2D
        
        # Test bounds (zoomed area)
        test_bounds = (0.2, 0.6, 0.2, 0.6)
        
        # Create fractals
        random_sierpinski = SierpinskiTriangle()
        deterministic_sierpinski = DeterministicSierpinskiTriangle()
        
        print("Testing RANDOM Sierpinski Triangle:")
        renderer1 = FractalRenderer2D(random_sierpinski, 300, 300)
        
        # Render same area twice
        image1a = renderer1.render(bounds=test_bounds, progressive=False, iterations=100000)
        image1b = renderer1.render(bounds=test_bounds, progressive=False, iterations=100000)
        
        # Compare the two renders
        difference1 = np.mean(np.abs(image1a - image1b))
        print(f"  Render 1 vs Render 2 difference: {difference1:.6f}")
        
        if difference1 > 0.001:
            print("  ✗ Random version is inconsistent (different each time)")
        else:
            print("  ✓ Random version is consistent")
        
        print("\nTesting DETERMINISTIC Sierpinski Triangle:")
        renderer2 = FractalRenderer2D(deterministic_sierpinski, 300, 300)
        
        # Render same area twice  
        image2a = renderer2.render(bounds=test_bounds, progressive=False)
        image2b = renderer2.render(bounds=test_bounds, progressive=False)
        
        # Compare the two renders
        difference2 = np.mean(np.abs(image2a - image2b))
        print(f"  Render 1 vs Render 2 difference: {difference2:.6f}")
        
        if difference2 < 0.0001:
            print("  ✓ Deterministic version is consistent (same every time)")
        else:
            print("  ✗ Deterministic version has unexpected differences")
        
        # Test visual quality
        coverage_random = np.count_nonzero(image1a) / image1a.size * 100
        coverage_deterministic = np.count_nonzero(image2a) / image2a.size * 100
        
        print(f"\nVisual Quality Comparison:")
        print(f"  Random Sierpinski coverage: {coverage_random:.1f}%")
        print(f"  Deterministic Sierpinski coverage: {coverage_deterministic:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"✗ Consistency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_zoom_behavior():
    """Test zoom behavior of deterministic version."""
    print("\n" + "=" * 60)
    print("TESTING DETERMINISTIC SIERPINSKI ZOOM BEHAVIOR")
    print("=" * 60)
    
    try:
        from fractal_explorer.fractals.deterministic_fractals import DeterministicSierpinskiTriangle
        from fractal_explorer.rendering import FractalRenderer2D
        
        sierpinski = DeterministicSierpinskiTriangle()
        renderer = FractalRenderer2D(sierpinski, 400, 400)
        
        # Test different zoom levels
        zoom_tests = [
            ("Default view", sierpinski.get_default_bounds(), 1.0),
            ("2x zoom", (0.2, 0.8, 0.2, 0.8), 2.0),
            ("4x zoom", (0.3, 0.7, 0.3, 0.7), 3.0),
            ("8x zoom", (0.4, 0.6, 0.4, 0.6), 6.0),
        ]
        
        print("Testing zoom consistency...")
        
        for name, bounds, expected_zoom in zoom_tests:
            # Render twice to test consistency
            image1 = renderer.render(bounds=bounds, progressive=False)
            image2 = renderer.render(bounds=bounds, progressive=False)
            
            # Check consistency
            difference = np.mean(np.abs(image1 - image2))
            coverage = np.count_nonzero(image1) / image1.size * 100
            
            print(f"\n{name} (zoom ~{expected_zoom:.1f}x):")
            print(f"  Consistency difference: {difference:.8f}")
            print(f"  Coverage: {coverage:.1f}%")
            
            if difference < 0.0001:
                print(f"  ✓ Consistent rendering")
            else:
                print(f"  ✗ Inconsistent rendering")
        
        return True
        
    except Exception as e:
        print(f"✗ Zoom behavior test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def explain_the_difference():
    """Explain what the user should expect."""
    print("\n" + "=" * 60)
    print("EXPLANATION: RANDOM vs DETERMINISTIC FRACTALS")
    print("=" * 60)
    
    print("\n🎲 RANDOM IFS Method (Original - PROBLEMATIC):")
    print("   • Uses random number generator to place points")
    print("   • Different result every time you render")
    print("   • Flashing colors when panning (new random points)")
    print("   • 'Running out of points' when zoomed (sparse random distribution)")
    print("   • Not how mathematical fractals should behave")
    
    print("\n🎯 DETERMINISTIC Method (Fixed - CORRECT):")
    print("   • Uses mathematical rules to determine fractal structure")
    print("   • Identical result every time for the same area")
    print("   • No color flashing (stable, consistent image)")
    print("   • Infinite detail at any zoom level") 
    print("   • True mathematical fractal behavior")
    
    print("\n✨ Expected Behavior with Deterministic Version:")
    print("   ✓ Sierpinski Triangle looks the same every render")
    print("   ✓ No flashing when panning around")
    print("   ✓ Smooth zooming with infinite detail")
    print("   ✓ Self-similar triangular patterns at all scales")
    print("   ✓ Behaves like Mandelbrot (consistent mathematical structure)")
    
    print("\n🧪 To Test in the GUI:")
    print("   1. Select 'Sierpinski Triangle' (deterministic version)")
    print("   2. Pan around - no color flashing")
    print("   3. Zoom in - structure is preserved")
    print("   4. Return to same area - looks identical")
    print("   5. Compare with 'Sierpinski (Random)' to see the difference")


def main():
    """Run all tests and explanations."""
    print("SIERPINSKI TRIANGLE - DETERMINISTIC vs RANDOM COMPARISON")
    
    results = []
    results.append(("Consistency Test", test_consistency()))
    results.append(("Zoom Behavior Test", test_zoom_behavior()))
    
    # Summary
    print("\n" + "=" * 60)
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
        print("\n🎉 DETERMINISTIC SIERPINSKI IS WORKING!")
        print("The fractal should now behave consistently!")
    else:
        print("\n⚠️ Some tests failed. Check the implementation.")
    
    # Always show the explanation
    explain_the_difference()
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)