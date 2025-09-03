#!/usr/bin/env python3
"""Test script to verify the render keyword argument fix."""

import sys
import os

# Set up paths and environment
sys.path.insert(0, os.path.abspath('.'))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

def test_render_fix():
    """Test that the render method no longer has keyword argument conflicts."""
    
    print("Testing render method keyword argument fix...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app = QApplication([])
        
        # Import components
        from fractal_explorer.ui.main_window import FractalExplorerWindow
        from fractal_explorer.fractals import MandelbrotSet
        from fractal_explorer.rendering import FractalRenderer2D
        
        print("1. Creating main window...")
        window = FractalExplorerWindow()
        print("   ✓ Window created")
        
        print("2. Testing manual render call...")
        # This simulates what happens when the user triggers a render
        if window.renderer:
            settings = window.control_panel.get_render_settings()
            print(f"   Settings: {list(settings.keys())}")
            
            # This is the fixed render call that should not cause conflicts
            progressive = settings.pop('progressive', True)
            bounds = settings.pop('bounds', None)
            image = window.renderer.render(bounds=bounds, progressive=progressive, **settings)
            print(f"   ✓ Manual render successful: {image.shape}")
        
        print("3. Testing _render_fractal method...")
        # This tests the actual method that was causing the error
        window._initializing = False  # Make sure we're not in init mode
        
        try:
            window._render_fractal()
            print("   ✓ _render_fractal method successful")
        except Exception as e:
            print(f"   ✗ _render_fractal failed: {e}")
            return False
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING RENDER KEYWORD ARGUMENT FIX")
    print("=" * 60)
    
    success = test_render_fix()
    
    if success:
        print("\n✓ All render tests passed!")
        print("The 'multiple values for keyword argument' error should be fixed.")
        print("\nYou can now run: python -m fractal_explorer.main")
    else:
        print("\n✗ Render tests failed!")
        print("The keyword argument issue may still exist.")
    
    sys.exit(0 if success else 1)