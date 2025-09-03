"""Main application class for Fractal Explorer."""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from .ui.main_window import FractalExplorerWindow


class FractalExplorer:
    """Main application class."""
    
    def __init__(self):
        """Initialize the application."""
        self.app = None
        self.window = None
        
    def run(self):
        """Run the application."""
        # Enable high DPI support BEFORE creating QApplication
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Create Qt application
        self.app = QApplication(sys.argv)
        
        # Set application properties
        self.app.setApplicationName("Fractal Explorer")
        self.app.setOrganizationName("FractalExplorer")
        
        # Create and show main window
        self.window = FractalExplorerWindow()
        self.window.show()
        
        # Run event loop
        return self.app.exec_()
    
    @staticmethod
    def version():
        """Get application version."""
        return "0.1.0"