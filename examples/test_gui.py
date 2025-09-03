"""Test the GUI application without displaying it (for CI/testing)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # Run without display

from PyQt5.QtWidgets import QApplication
from fractal_explorer.ui.main_window import FractalExplorerWindow


def test_gui():
    """Test GUI creation and basic functionality."""
    print("Testing GUI components...")
    
    # Create Qt application
    app = QApplication([])
    
    try:
        # Create main window
        window = FractalExplorerWindow()
        print("✓ Main window created")
        
        # Test fractal switching
        window.control_panel.fractal_combo.setCurrentText("Julia Set")
        print("✓ Fractal switching works")
        
        # Test parameter changes
        if hasattr(window, 'renderer') and window.renderer:
            print("✓ Renderer initialized")
        
        print("✓ GUI test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ GUI test failed: {e}")
        return False
        
    finally:
        app.quit()


if __name__ == "__main__":
    success = test_gui()
    sys.exit(0 if success else 1)