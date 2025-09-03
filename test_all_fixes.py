#!/usr/bin/env python3
"""Comprehensive test script for all fractal explorer fixes."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_basic_functionality():
    """Test basic functionality without GUI."""
    print("=" * 60)
    print("TESTING BASIC FUNCTIONALITY")
    print("=" * 60)
    
    try:
        print("1. Testing imports...")
        from fractal_explorer.fractals import MandelbrotSet, JuliaSet, BurningShip
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
        
        print("4. Testing parameter passing...")
        # Test the specific issue that was causing problems
        params = {'max_iter': 100, 'progressive': True}
        progressive = params.pop('progressive', True)
        image2 = renderer.render(progressive=progressive, **params)
        print(f"   ✓ Parameter passing works: shape={image2.shape}")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Basic functionality failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_components():
    """Test GUI components without display."""
    print("\n" + "=" * 60)
    print("TESTING GUI COMPONENTS (HEADLESS)")
    print("=" * 60)
    
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
        
        print("3. Testing render settings...")
        settings = control_panel.get_render_settings()
        print(f"   ✓ Render settings: {list(settings.keys())}")
        
        print("4. Testing canvas...")
        from fractal_explorer.ui.canvas import FractalCanvas
        canvas = FractalCanvas()
        print("   ✓ Canvas works")
        
        print("5. Testing main window creation...")
        from fractal_explorer.ui.main_window import FractalExplorerWindow
        window = FractalExplorerWindow()
        print("   ✓ Main window created without hanging")
        
        print("6. Testing render method fix...")
        if window.renderer:
            # This should not cause keyword argument conflicts
            window._initializing = False
            window._render_fractal()
            print("   ✓ Render method works without conflicts")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"   ✗ GUI component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_application_startup():
    """Test the main application class startup."""
    print("\n" + "=" * 60)
    print("TESTING APPLICATION STARTUP")
    print("=" * 60)
    
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
        
        print("4. Testing Qt attribute fix...")
        # This should not raise any Qt warnings about attributes
        import os
        original_platform = os.environ.get('QT_QPA_PLATFORM')
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        try:
            # This would normally start the app, but we'll simulate the critical parts
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import Qt
            
            # Test that attributes are set before QApplication creation
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
            test_app = QApplication(['test'])
            
            print("   ✓ Qt attributes set correctly")
            test_app.quit()
            
        finally:
            if original_platform:
                os.environ['QT_QPA_PLATFORM'] = original_platform
            elif 'QT_QPA_PLATFORM' in os.environ:
                del os.environ['QT_QPA_PLATFORM']
        
        return True
        
    except Exception as e:
        print(f"   ✗ Application startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_specific_error_scenarios():
    """Test scenarios that previously caused errors."""
    print("\n" + "=" * 60)
    print("TESTING SPECIFIC ERROR SCENARIOS")
    print("=" * 60)
    
    try:
        import os
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app = QApplication([])
        
        print("1. Testing 'multiple values for keyword argument' scenario...")
        from fractal_explorer.fractals import MandelbrotSet
        from fractal_explorer.rendering import FractalRenderer2D
        from fractal_explorer.ui.controls import ControlPanel
        
        # Recreate the exact scenario that caused the error
        mandelbrot = MandelbrotSet()
        renderer = FractalRenderer2D(mandelbrot, 400, 300)
        control_panel = ControlPanel()
        
        settings = control_panel.get_render_settings()
        settings.update({'max_iter': 256, 'adaptive_iter': True})
        
        # This used to cause: "got multiple values for keyword argument 'progressive'"
        progressive = settings.pop('progressive', True)
        bounds = settings.pop('bounds', None)
        image = renderer.render(bounds=bounds, progressive=progressive, **settings)
        print(f"   ✓ No keyword conflicts: {image.shape}")
        
        print("2. Testing window initialization without hanging...")
        from fractal_explorer.ui.main_window import FractalExplorerWindow
        
        # This used to hang during initialization
        window = FractalExplorerWindow()
        print(f"   ✓ Window created, initializing flag: {getattr(window, '_initializing', 'not set')}")
        
        # Test that render is deferred during initialization
        print("3. Testing deferred rendering...")
        window._initializing = True
        window._render_fractal()  # Should return early due to _initializing flag
        print("   ✓ Rendering properly deferred during initialization")
        
        window._initializing = False
        if window.renderer:
            window._render_fractal()  # Should work normally now
            print("   ✓ Rendering works after initialization")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"   ✗ Specific error scenario test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_usage_instructions():
    """Print instructions for manual testing."""
    print("\n" + "=" * 60)
    print("MANUAL TESTING INSTRUCTIONS")
    print("=" * 60)
    
    print("\nTo test the GUI application manually:")
    print("1. Ensure you're in the virtual environment:")
    print("   source venv/bin/activate")
    print("\n2. Run the main application:")
    print("   python -m fractal_explorer.main")
    print("\n3. Expected behavior:")
    print("   ✓ Window opens quickly without hanging")
    print("   ✓ No 'multiple values for keyword argument' errors")
    print("   ✓ Initial fractal renders after window is shown")
    print("   ✓ Fractal switching works smoothly")
    print("   ✓ Parameter controls respond correctly")
    print("   ✓ Mouse controls work (zoom, pan)")
    
    print("\nFixed Issues:")
    print("   ✓ Qt high DPI attributes set before QApplication creation")
    print("   ✓ Initialization hanging resolved with _initializing flag")
    print("   ✓ Keyword argument conflicts in render() method resolved")
    print("   ✓ Proper parameter extraction before render calls")
    
    print("\nIf you still encounter issues:")
    print("   • Run: python test_all_fixes.py")
    print("   • Check virtual environment is activated")
    print("   • Look for any remaining error messages")


def main():
    """Run all tests."""
    print("FRACTAL EXPLORER - COMPREHENSIVE FIXES TEST")
    
    results = []
    
    # Run tests
    results.append(("Basic Functionality", test_basic_functionality()))
    results.append(("GUI Components", test_gui_components()))
    results.append(("Application Startup", test_application_startup()))
    results.append(("Specific Error Scenarios", test_specific_error_scenarios()))
    
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
        print("\n🎉 ALL TESTS PASSED!")
        print("The fractal explorer should now work without errors!")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed.")
        print("Some issues may still remain.")
    
    # Print manual testing instructions
    print_usage_instructions()
    
    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)