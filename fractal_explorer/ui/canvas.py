"""Interactive canvas widget for fractal visualization."""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QPoint, QTimer
from PyQt5.QtGui import QPainter, QImage, QPen, QColor, QWheelEvent
import numpy as np
from typing import Optional, Tuple


class FractalCanvas(QWidget):
    """Interactive canvas for displaying and manipulating fractals."""
    
    # Signals
    zoom_changed = pyqtSignal(float)  # Emits new zoom level
    bounds_changed = pyqtSignal(tuple)  # Emits new bounds
    render_requested = pyqtSignal()  # Request new render
    
    def __init__(self, parent=None):
        """Initialize the fractal canvas."""
        super().__init__(parent)
        
        # Canvas state
        self.image_data = None
        self.qimage = None
        
        # Interaction state
        self.mouse_pressed = False
        self.pan_start = None
        self.selection_start = None
        self.selection_rect = None
        self.is_selecting = False
        self.is_panning = False
        
        # Rendering state
        self.renderer = None
        
        # Setup
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMinimumSize(400, 300)
        
        # Double buffering for smooth updates
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        
    def set_renderer(self, renderer):
        """Set the fractal renderer.
        
        Args:
            renderer: FractalRenderer2D instance
        """
        self.renderer = renderer
        
    def set_image(self, image_data: np.ndarray):
        """Set the image data to display.
        
        Args:
            image_data: RGB image array (height, width, 3)
        """
        self.image_data = image_data
        self._update_qimage()
        self.update()
        
    def _update_qimage(self):
        """Convert numpy array to QImage."""
        if self.image_data is None:
            return
            
        height, width = self.image_data.shape[:2]
        
        # Convert to uint8
        img_uint8 = (self.image_data * 255).astype(np.uint8)
        
        # Ensure contiguous array
        if not img_uint8.flags['C_CONTIGUOUS']:
            img_uint8 = np.ascontiguousarray(img_uint8)
            
        # Create QImage
        self.qimage = QImage(img_uint8.data, width, height, 
                            width * 3, QImage.Format_RGB888)
        
    def paintEvent(self, event):
        """Paint the canvas."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), Qt.black)
        
        # Draw fractal image
        if self.qimage:
            # Scale image to fit widget
            scaled_img = self.qimage.scaled(self.size(), 
                                           Qt.KeepAspectRatio,
                                           Qt.SmoothTransformation)
            
            # Center the image
            x = (self.width() - scaled_img.width()) // 2
            y = (self.height() - scaled_img.height()) // 2
            painter.drawImage(x, y, scaled_img)
        
        # Draw selection rectangle
        if self.is_selecting and self.selection_rect:
            pen = QPen(QColor(255, 255, 0), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.selection_rect)
            
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            
            if event.modifiers() & Qt.ShiftModifier:
                # Start rectangle selection for zoom
                self.is_selecting = True
                self.selection_start = event.pos()
                self.selection_rect = QRect(event.pos(), event.pos())
            else:
                # Start panning
                self.is_panning = True
                self.pan_start = event.pos()
                self.setCursor(Qt.ClosedHandCursor)
                
        elif event.button() == Qt.RightButton:
            # Reset view
            if self.renderer:
                self.renderer.reset_view()
                self.render_requested.emit()
                
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.mouse_pressed:
            if self.is_selecting:
                # Update selection rectangle
                self.selection_rect = QRect(self.selection_start, event.pos()).normalized()
                self.update()
                
            elif self.is_panning and self.pan_start:
                # Pan the view
                delta = event.pos() - self.pan_start
                
                if self.renderer:
                    # Convert widget coordinates to image coordinates
                    img_width = self.image_data.shape[1] if self.image_data is not None else self.width()
                    img_height = self.image_data.shape[0] if self.image_data is not None else self.height()
                    
                    dx = -delta.x() * (img_width / self.width())
                    dy = -delta.y() * (img_height / self.height())
                    
                    self.renderer.pan(dx, dy)
                    self.pan_start = event.pos()
                    self.render_requested.emit()
                    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False
            
            if self.is_selecting and self.selection_rect:
                # Zoom to selected rectangle
                if self.renderer and self.selection_rect.width() > 10 and self.selection_rect.height() > 10:
                    # Convert widget coordinates to image coordinates
                    img_width = self.image_data.shape[1] if self.image_data is not None else self.width()
                    img_height = self.image_data.shape[0] if self.image_data is not None else self.height()
                    
                    x1 = self.selection_rect.left() * (img_width / self.width())
                    y1 = self.selection_rect.top() * (img_height / self.height())
                    x2 = self.selection_rect.right() * (img_width / self.width())
                    y2 = self.selection_rect.bottom() * (img_height / self.height())
                    
                    self.renderer.zoom_rectangle(int(x1), int(y1), int(x2), int(y2))
                    self.render_requested.emit()
                    
                self.is_selecting = False
                self.selection_rect = None
                self.update()
                
            if self.is_panning:
                self.is_panning = False
                self.setCursor(Qt.ArrowCursor)
                
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for zooming."""
        if self.renderer:
            # Get mouse position in widget
            pos = event.pos()
            
            # Convert to image coordinates
            img_width = self.image_data.shape[1] if self.image_data is not None else self.width()
            img_height = self.image_data.shape[0] if self.image_data is not None else self.height()
            
            x = pos.x() * (img_width / self.width())
            y = pos.y() * (img_height / self.height())
            
            # Calculate zoom factor
            delta = event.angleDelta().y()
            zoom_factor = 1.2 if delta > 0 else 0.8
            
            # Apply zoom
            self.renderer.zoom(x, y, zoom_factor)
            self.render_requested.emit()
            
    def keyPressEvent(self, event):
        """Handle keyboard events."""
        if not self.renderer:
            return
            
        step = 50  # Pan step in pixels
        
        if event.key() == Qt.Key_Left:
            self.renderer.pan(-step, 0)
            self.render_requested.emit()
        elif event.key() == Qt.Key_Right:
            self.renderer.pan(step, 0)
            self.render_requested.emit()
        elif event.key() == Qt.Key_Up:
            self.renderer.pan(0, -step)
            self.render_requested.emit()
        elif event.key() == Qt.Key_Down:
            self.renderer.pan(0, step)
            self.render_requested.emit()
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.renderer.zoom(self.width() // 2, self.height() // 2, 1.5)
            self.render_requested.emit()
        elif event.key() == Qt.Key_Minus:
            self.renderer.zoom(self.width() // 2, self.height() // 2, 0.67)
            self.render_requested.emit()
        elif event.key() == Qt.Key_R:
            self.renderer.reset_view()
            self.render_requested.emit()
        elif event.key() == Qt.Key_C:
            # Cycle color palette
            if self.renderer:
                self.renderer.color_mapper.cycle_palette()
                self.render_requested.emit()
                
    def resizeEvent(self, event):
        """Handle widget resize."""
        if self.renderer:
            # Update renderer dimensions
            self.renderer.width = event.size().width()
            self.renderer.height = event.size().height()
            self.render_requested.emit()
            
        super().resizeEvent(event)