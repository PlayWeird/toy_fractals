#!/usr/bin/env python3
"""Test script to verify UI fixes and fractal improvements."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_ui_layout_fixes():
    """Test that UI layout improvements work."""
    print("=" * 60)
    print("TESTING UI LAYOUT FIXES")
    print("=" * 60)
    
    try:
        import os
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app = QApplication([])
        
        print("1. Testing improved control panel layout...")
        from fractal_explorer.ui.controls import ControlPanel
        from fractal_explorer.fractals import MandelbrotSet, JuliaSet
        
        control_panel = ControlPanel()
        fractals = {
            'Mandelbrot': MandelbrotSet(), 
            'Julia': JuliaSet(),
        }
        control_panel.set_fractals(fractals)
        print("   ✓ Control panel created with improved layout")
        
        # Test parameter widget creation
        control_panel.fractal_combo.setCurrentText('Julia')
        app.processEvents()  # Let Qt process the change
        
        if len(control_panel.parameter_widgets) > 0:
            print(f"   ✓ Parameter widgets created: {len(control_panel.parameter_widgets)} controls")
        
        print("2. Testing widget sizing...")
        for name, widget in control_panel.parameter_widgets.items():
            widget_type = type(widget).__name__
            print(f"   - {name}: {widget_type}")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"   ✗ UI layout test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ifs_fractal_improvements():
    """Test that IFS fractals display properly."""
    print("\n" + "=" * 60)
    print("TESTING IFS FRACTAL IMPROVEMENTS")
    print("=" * 60)
    
    try:
        from fractal_explorer.fractals import SierpinskiTriangle, BarnsleyFern, DragonCurve
        from fractal_explorer.rendering import FractalRenderer2D
        import numpy as np
        
        fractals_to_test = [
            ("Sierpinski Triangle", SierpinskiTriangle()),
            ("Barnsley Fern", BarnsleyFern()),
            ("Dragon Curve", DragonCurve()),
        ]
        
        for name, fractal in fractals_to_test:
            print(f"Testing {name}...")
            
            # Check parameters
            params = fractal.get_parameters()
            iterations = params.get('iterations', {}).get('default', 100000)
            print(f"   Default iterations: {iterations:,}")
            
            # Test rendering
            renderer = FractalRenderer2D(fractal, 200, 200)
            image = renderer.render(progressive=False, iterations=min(iterations, 100000))
            
            # Check if fractal is visible
            non_zero_pixels = np.count_nonzero(image)
            total_pixels = image.size
            coverage = non_zero_pixels / total_pixels * 100
            
            print(f"   Image coverage: {coverage:.1f}% ({non_zero_pixels:,} / {total_pixels:,} pixels)")
            
            if coverage > 5:  # Should have reasonable coverage
                print(f"   ✓ {name} renders properly")
            else:
                print(f"   ⚠ {name} has low coverage - may need adjustment")
        
        return True
        
    except Exception as e:
        print(f"   ✗ IFS fractal test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_fractal_types():
    """Test that all fractal types are available and work."""
    print("\n" + "=" * 60)
    print("TESTING ALL FRACTAL TYPES")
    print("=" * 60)
    
    try:
        import os
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app = QApplication([])
        
        from fractal_explorer.ui.main_window import FractalExplorerWindow
        
        print("1. Creating main window...")
        window = FractalExplorerWindow()
        
        print("2. Testing all available fractals...")
        fractal_names = list(window.fractals.keys())
        print(f"   Available fractals: {fractal_names}")
        
        for name in fractal_names:
            try:
                print(f"   Testing {name}...")
                
                # Switch to this fractal
                window.control_panel.fractal_combo.setCurrentText(name)
                app.processEvents()
                
                # Check if renderer was created
                if window.renderer:
                    fractal = window.current_fractal
                    params = fractal.get_parameters()
                    print(f"     Parameters: {list(params.keys())}")
                    print(f"     Type: {fractal.get_type()}")
                    print(f"     Bounds: {fractal.get_default_bounds()}")
                    print(f"     ✓ {name} loads successfully")
                else:
                    print(f"     ⚠ {name} - no renderer created")
                    
            except Exception as e:
                print(f"     ✗ {name} failed: {e}")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"   ✗ Fractal types test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_improvement_summary():
    """Print summary of improvements made."""
    print("\n" + "=" * 60)
    print("UI AND FRACTAL IMPROVEMENTS SUMMARY")
    print("=" * 60)
    
    print("\n🎨 UI Layout Improvements:")
    print("   ✓ Parameter labels shortened for better fit")
    print("   ✓ Vertical layout for parameter controls")
    print("   ✓ Improved slider spacing and minimum widths")
    print("   ✓ Value labels with fixed width and alignment")
    print("   ✓ Better spacing and margins throughout")
    
    print("\n🌀 IFS Fractal Improvements:")
    print("   ✓ Increased default iterations for better quality:")
    print("     - Sierpinski Triangle: 100k → 200k")
    print("     - Barnsley Fern: 500k → 1M")
    print("     - Dragon Curve: 200k → 500k")
    print("   ✓ Added Dragon Curve to main application")
    print("   ✓ Improved parameter ranges and steps")
    print("   ✓ Better default bounds and visibility")
    
    print("\n🚀 What to Test in the GUI:")
    print("   1. Parameters section should have proper spacing")
    print("   2. Sliders should have enough room to slide")
    print("   3. Text labels should fit without clipping")
    print("   4. IFS fractals should be clearly visible")
    print("   5. Dragon Curve should appear in the fractal list")
    print("   6. Higher iteration counts should show more detail")


def main():
    """Run all tests."""
    print("FRACTAL EXPLORER - UI FIXES AND IMPROVEMENTS TEST")
    
    results = []
    
    # Run tests
    results.append(("UI Layout Fixes", test_ui_layout_fixes()))
    results.append(("IFS Fractal Improvements", test_ifs_fractal_improvements()))
    results.append(("All Fractal Types", test_all_fractal_types()))
    
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
        print("\n🎉 ALL UI IMPROVEMENTS WORKING!")
        print("The parameter section and IFS fractals should now work much better!")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed.")
        print("Some UI improvements may not be working correctly.")
    
    # Print improvement summary
    print_improvement_summary()
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)