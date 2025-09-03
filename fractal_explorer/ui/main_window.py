"""Main application window for the fractal explorer."""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                            QMenuBar, QMenu, QAction, QStatusBar, QMessageBox,
                            QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QKeySequence
import numpy as np
import time

from .canvas import FractalCanvas
from .controls import ControlPanel
from ..rendering import FractalRenderer2D
from ..fractals import (MandelbrotSet, JuliaSet, BurningShip,
                        SierpinskiTriangle, BarnsleyFern)


class RenderThread(QThread):
    """Background thread for fractal rendering."""
    
    finished = pyqtSignal(np.ndarray)
    progress = pyqtSignal(int)
    
    def __init__(self, renderer, bounds, params):
        super().__init__()
        self.renderer = renderer
        self.bounds = bounds
        self.params = params
        
    def run(self):
        """Run the rendering process."""
        try:
            image = self.renderer.render(self.bounds, **self.params)
            self.finished.emit(image)
        except Exception as e:
            print(f"Render error: {e}")


class FractalExplorerWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Available fractals
        self.fractals = {
            'Mandelbrot Set': MandelbrotSet(),
            'Julia Set': JuliaSet(),
            'Burning Ship': BurningShip(),
            'Sierpinski Triangle': SierpinskiTriangle(),
            'Barnsley Fern': BarnsleyFern(),
        }
        
        # Current state
        self.current_fractal = None
        self.renderer = None
        self.render_thread = None
        self.render_params = {}
        
        # Setup UI
        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()
        
        # Initialize with first fractal
        first_fractal = list(self.fractals.keys())[0]
        self.control_panel.set_fractals(self.fractals)
        self.control_panel.fractal_combo.setCurrentText(first_fractal)
        
    def _setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Fractal Explorer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with splitter
        layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)
        
        # Control panel
        self.control_panel = ControlPanel()
        self.control_panel.fractal_changed.connect(self._on_fractal_changed)
        self.control_panel.parameter_changed.connect(self._on_parameter_changed)
        self.control_panel.render_requested.connect(self._render_fractal)
        self.control_panel.save_requested.connect(self._save_image)
        
        # Canvas
        self.canvas = FractalCanvas()
        self.canvas.render_requested.connect(self._render_fractal)
        
        # Add to splitter
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.canvas)
        splitter.setSizes([300, 900])
        
        layout.addWidget(splitter)
        central_widget.setLayout(layout)
        
    def _setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        save_action = QAction('Save Image', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(lambda: self._save_image())
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        reset_action = QAction('Reset View', self)
        reset_action.setShortcut('R')
        reset_action.triggered.connect(self._reset_view)
        view_menu.addAction(reset_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self._zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self._zoom_out)
        view_menu.addAction(zoom_out_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
        shortcuts_action = QAction('Keyboard Shortcuts', self)
        shortcuts_action.triggered.connect(self._show_shortcuts)
        help_menu.addAction(shortcuts_action)
        
    def _setup_statusbar(self):
        """Setup the status bar."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.statusbar.showMessage("Ready")
        
    def _on_fractal_changed(self, name: str):
        """Handle fractal type change."""
        if name in self.fractals:
            self.current_fractal = self.fractals[name]
            
            # Create new renderer
            self.renderer = FractalRenderer2D(
                self.current_fractal,
                self.canvas.width(),
                self.canvas.height()
            )
            
            # Set renderer in canvas
            self.canvas.set_renderer(self.renderer)
            
            # Reset parameters
            self.render_params = {}
            
            # Render
            self._render_fractal()
            
    def _on_parameter_changed(self, name: str, value):
        """Handle parameter change."""
        if name == 'palette':
            if self.renderer:
                self.renderer.color_mapper.palette = value
                self._update_display()
        elif name == 'invert_colors':
            if self.renderer:
                self.renderer.color_mapper.invert = value
                self._update_display()
        elif name == 'reset_view':
            self._reset_view()
        else:
            self.render_params[name] = value
            # Auto-render for small changes
            if name in ['c_real', 'c_imag']:
                self._render_fractal()
                
    def _render_fractal(self):
        """Render the current fractal."""
        if not self.renderer:
            return
            
        # Update status
        self.statusbar.showMessage("Rendering...")
        self.control_panel.update_status("Rendering...")
        
        # Get render settings
        settings = self.control_panel.get_render_settings()
        settings.update(self.render_params)
        
        # Start render
        start_time = time.time()
        
        try:
            # Render fractal
            image = self.renderer.render(progressive=settings.get('progressive', True),
                                        **settings)
            
            # Update canvas
            self.canvas.set_image(image)
            
            # Update status
            render_time = time.time() - start_time
            stats = self.renderer.get_stats()
            
            status_msg = (f"Rendered in {render_time:.2f}s | "
                         f"Zoom: {stats['zoom_level']:.1f}x | "
                         f"Center: ({stats['center'][0]:.6f}, {stats['center'][1]:.6f})")
            
            self.statusbar.showMessage(status_msg)
            self.control_panel.update_status(f"Render time: {render_time:.2f}s")
            
        except Exception as e:
            QMessageBox.critical(self, "Render Error", f"Failed to render fractal: {str(e)}")
            self.statusbar.showMessage("Render failed")
            self.control_panel.update_status("Error: " + str(e))
            
    def _update_display(self):
        """Update display without re-rendering fractal data."""
        if self.renderer and self.renderer.current_data is not None:
            image = self.renderer.color_mapper.get_colors(self.renderer.current_data)
            self.canvas.set_image(image)
            
    def _save_image(self, filename: str = None):
        """Save the current fractal image."""
        if not self.renderer:
            return
            
        if not filename:
            from PyQt5.QtWidgets import QFileDialog
            filename, _ = QFileDialog.getSaveFileName(
                self, "Save Fractal Image", "",
                "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)")
                
        if filename:
            try:
                # Ask for high resolution option
                reply = QMessageBox.question(self, "Save Options",
                                           "Save at high resolution (2x)?",
                                           QMessageBox.Yes | QMessageBox.No,
                                           QMessageBox.No)
                
                high_res = (reply == QMessageBox.Yes)
                self.renderer.save_image(filename, high_res=high_res)
                
                self.statusbar.showMessage(f"Image saved to {filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save image: {str(e)}")
                
    def _reset_view(self):
        """Reset to default view."""
        if self.renderer:
            self.renderer.reset_view()
            self._render_fractal()
            
    def _zoom_in(self):
        """Zoom in at center."""
        if self.renderer:
            cx = self.canvas.width() // 2
            cy = self.canvas.height() // 2
            self.renderer.zoom(cx, cy, 1.5)
            self._render_fractal()
            
    def _zoom_out(self):
        """Zoom out at center."""
        if self.renderer:
            cx = self.canvas.width() // 2
            cy = self.canvas.height() // 2
            self.renderer.zoom(cx, cy, 0.67)
            self._render_fractal()
            
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About Fractal Explorer",
                         "<h2>Fractal Explorer</h2>"
                         "<p>Version 0.1.0</p>"
                         "<p>An interactive multi-fractal visualization framework with "
                         "support for various fractal types and real-time exploration.</p>"
                         "<p>Features:</p>"
                         "<ul>"
                         "<li>Multiple fractal types (Mandelbrot, Julia, IFS, etc.)</li>"
                         "<li>Interactive zoom and pan</li>"
                         "<li>Customizable color palettes</li>"
                         "<li>High-resolution export</li>"
                         "</ul>")
                         
    def _show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        QMessageBox.information(self, "Keyboard Shortcuts",
                               "<h3>Keyboard Shortcuts</h3>"
                               "<table>"
                               "<tr><td><b>Mouse Drag:</b></td><td>Pan view</td></tr>"
                               "<tr><td><b>Shift + Drag:</b></td><td>Zoom to rectangle</td></tr>"
                               "<tr><td><b>Scroll Wheel:</b></td><td>Zoom in/out at cursor</td></tr>"
                               "<tr><td><b>Right Click:</b></td><td>Reset view</td></tr>"
                               "<tr><td><b>Arrow Keys:</b></td><td>Pan view</td></tr>"
                               "<tr><td><b>+/-:</b></td><td>Zoom in/out</td></tr>"
                               "<tr><td><b>R:</b></td><td>Reset view</td></tr>"
                               "<tr><td><b>C:</b></td><td>Cycle color palette</td></tr>"
                               "<tr><td><b>Ctrl+S:</b></td><td>Save image</td></tr>"
                               "</table>")