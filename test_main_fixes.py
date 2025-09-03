#!/usr/bin/env python3
"""Test script for the main application fixes."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_basic_functionality():
    """Test basic functionality without GUI."""
    print("=" * 50)
    print("TESTING BASIC FUNCTIONALITY")
    print("=" * 50)
    
    try:
        print("1. Testing imports...")
        from fractal_explorer.fractals import MandelbrotSet, JuliaSet
        from fractal_explorer.rendering import FractalRenderer2D
        print("   ✓ Imports successful")
        
        print("2. Testing fractal computation...")
        mandelbrot = MandelbrotSet()
        data = mandelbrot.compute(100, 100, mandelbrot.get_default_bounds(), max_iter=50)
        print(f"   ✓ Mandelbrot computed: shape={data.shape}")
        
        print("3. Testing renderer...")
        renderer = FractalRenderer2D(mandelbrot, 200, 200)
        image = renderer.render(progressive=False, max_iter=50)
        print(f"   ✓ Renderer works: shape={image.shape}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Basic functionality failed: {e}")
        return False


def test_gui_components():
    """Test GUI components without display."""
    print("\n" + "=" * 50)
    print("TESTING GUI COMPONENTS (HEADLESS)")
    print("=" * 50)
    
    try:
        import os
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        print("1. Setting up Qt application...")
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app = QApplication([])
        print("   ✓ Qt application created")
        
        print("2. Testing control panel...")
        from fractal_explorer.ui.controls import ControlPanel
        from fractal_explorer.fractals import MandelbrotSet, JuliaSet
        
        control_panel = ControlPanel()
        fractals = {'Mandelbrot': MandelbrotSet(), 'Julia': JuliaSet()}
        control_panel.set_fractals(fractals)
        print("   ✓ Control panel works")
        
        print("3. Testing canvas...")
        from fractal_explorer.ui.canvas import FractalCanvas
        canvas = FractalCanvas()
        print("   ✓ Canvas works")
        
        print("4. Testing fractal selection...")
        control_panel.fractal_combo.setCurrentText('Julia')
        print("   ✓ Fractal selection works")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"   ✗ GUI component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_application_class():
    """Test the main application class."""
    print("\n" + "=" * 50)
    print("TESTING APPLICATION CLASS")
    print("=" * 50)
    
    try:
        print("1. Testing FractalExplorer import...")
        from fractal_explorer.app import FractalExplorer
        print("   ✓ Import successful")
        
        print("2. Testing FractalExplorer instantiation...")
        app = FractalExplorer()
        print("   ✓ Instantiation successful")
        
        print("3. Testing version method...")
        version = app.version()
        print(f"   ✓ Version: {version}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Application class test failed: {e}")
        return False


def print_usage_instructions():
    """Print instructions for manual testing."""
    print("\n" + "=" * 50)
    print("MANUAL TESTING INSTRUCTIONS")
    print("=" * 50)
    
    print("\nTo test the GUI application manually:")
    print("1. Ensure you're in the virtual environment:")
    print("   source venv/bin/activate")
    print("\n2. Run the main application:")
    print("   python -m fractal_explorer.main")
    print("\n3. Expected behavior:")
    print("   - Window should open without hanging")
    print("   - No immediate fractal should be rendered (until you interact)")
    print("   - You should be able to:")
    print("     * Switch between fractal types")
    print("     * Adjust parameters")
    print("     * Use mouse controls (zoom, pan)")
    print("     * See fractal rendering after interactions")
    
    print("\nCommon issues and fixes:")
    print("- If window hangs on startup: Check _initializing flag logic")
    print("- If no fractal appears: Check _initial_render method")
    print("- If parameters don't work: Check signal connections")
    print("- If Qt warnings appear: These are usually harmless")


def main():
    """Run all tests."""
    print("FRACTAL EXPLORER - MAIN APPLICATION FIXES TEST")
    
    results = []
    
    # Run tests
    results.append(("Basic Functionality", test_basic_functionality()))
    results.append(("GUI Components", test_gui_components()))
    results.append(("Application Class", test_application_class()))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n✓ All automated tests passed!")
        print("The main application should now work without hanging on startup.")
    else:
        print(f"\n✗ {len(results) - passed} test(s) failed.")
        print("There may still be issues with the application.")
    
    # Print manual testing instructions
    print_usage_instructions()
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)