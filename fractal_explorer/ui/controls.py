"""Control panel for fractal parameters and settings."""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QComboBox, QSlider, QSpinBox, QDoubleSpinBox,
                            QPushButton, QGroupBox, QCheckBox, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Dict, Any


class ControlPanel(QWidget):
    """Control panel for adjusting fractal parameters."""
    
    # Signals
    fractal_changed = pyqtSignal(str)  # Fractal type changed
    parameter_changed = pyqtSignal(str, object)  # Parameter name and value
    render_requested = pyqtSignal()
    save_requested = pyqtSignal(str)  # Save with filename
    
    def __init__(self, parent=None):
        """Initialize the control panel."""
        super().__init__(parent)
        
        self.fractals = {}  # Will be populated with available fractals
        self.current_fractal = None
        self.parameter_widgets = {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Fractal selector
        selector_group = QGroupBox("Fractal Type")
        selector_layout = QVBoxLayout()
        
        self.fractal_combo = QComboBox()
        self.fractal_combo.currentTextChanged.connect(self._on_fractal_changed)
        selector_layout.addWidget(self.fractal_combo)
        
        selector_group.setLayout(selector_layout)
        layout.addWidget(selector_group)
        
        # Parameters group
        self.params_group = QGroupBox("Parameters")
        self.params_layout = QVBoxLayout()
        self.params_group.setLayout(self.params_layout)
        layout.addWidget(self.params_group)
        
        # Color settings
        color_group = QGroupBox("Color Settings")
        color_layout = QVBoxLayout()
        
        palette_layout = QHBoxLayout()
        palette_layout.addWidget(QLabel("Palette:"))
        self.palette_combo = QComboBox()
        self.palette_combo.addItems(['classic', 'fire', 'ocean', 'twilight', 
                                    'rainbow', 'monochrome', 'coolwarm'])
        self.palette_combo.currentTextChanged.connect(self._on_palette_changed)
        palette_layout.addWidget(self.palette_combo)
        color_layout.addLayout(palette_layout)
        
        self.invert_check = QCheckBox("Invert Colors")
        self.invert_check.stateChanged.connect(self._on_invert_changed)
        color_layout.addWidget(self.invert_check)
        
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # Rendering options
        render_group = QGroupBox("Rendering")
        render_layout = QVBoxLayout()
        
        self.progressive_check = QCheckBox("Progressive Rendering")
        self.progressive_check.setChecked(True)
        render_layout.addWidget(self.progressive_check)
        
        self.adaptive_check = QCheckBox("Adaptive Iterations")
        self.adaptive_check.setChecked(True)
        render_layout.addWidget(self.adaptive_check)
        
        render_group.setLayout(render_layout)
        layout.addWidget(render_group)
        
        # Action buttons
        button_layout = QVBoxLayout()
        
        self.render_btn = QPushButton("Render")
        self.render_btn.clicked.connect(self.render_requested.emit)
        button_layout.addWidget(self.render_btn)
        
        self.reset_btn = QPushButton("Reset View")
        self.reset_btn.clicked.connect(self._on_reset_view)
        button_layout.addWidget(self.reset_btn)
        
        self.save_btn = QPushButton("Save Image")
        self.save_btn.clicked.connect(self._on_save_image)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # Status display
        self.status_label = QLabel("Ready")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        self.setLayout(layout)
        self.setMaximumWidth(300)
        
    def set_fractals(self, fractals: Dict[str, Any]):
        """Set available fractals.
        
        Args:
            fractals: Dictionary of fractal name -> fractal instance
        """
        self.fractals = fractals
        self.fractal_combo.clear()
        self.fractal_combo.addItems(list(fractals.keys()))
        
    def _on_fractal_changed(self, name: str):
        """Handle fractal type change."""
        if name in self.fractals:
            self.current_fractal = self.fractals[name]
            self._update_parameters()
            self.fractal_changed.emit(name)
            
    def _update_parameters(self):
        """Update parameter widgets based on current fractal."""
        # Clear existing parameter widgets
        for widget in self.parameter_widgets.values():
            widget.setParent(None)
        self.parameter_widgets.clear()
        
        # Clear layout
        while self.params_layout.count():
            item = self.params_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                
        if not self.current_fractal:
            return
            
        # Get fractal parameters
        params = self.current_fractal.get_parameters()
        
        # Create widgets for each parameter
        for param_name, param_info in params.items():
            param_layout = QHBoxLayout()
            
            # Label
            label = QLabel(f"{param_info.get('description', param_name)}:")
            label.setToolTip(param_info.get('description', ''))
            param_layout.addWidget(label)
            
            # Create appropriate widget based on type
            param_type = param_info['type']
            default = param_info.get('default', 0)
            
            if param_type == int:
                if 'min' in param_info and 'max' in param_info:
                    # Use slider for bounded integers
                    widget = QSlider(Qt.Horizontal)
                    widget.setMinimum(param_info['min'])
                    widget.setMaximum(param_info['max'])
                    widget.setValue(default)
                    widget.setTickPosition(QSlider.TicksBelow)
                    
                    # Add value label
                    value_label = QLabel(str(default))
                    widget.valueChanged.connect(
                        lambda v, l=value_label, p=param_name: self._on_slider_changed(v, l, p)
                    )
                    param_layout.addWidget(widget)
                    param_layout.addWidget(value_label)
                else:
                    # Use spinbox
                    widget = QSpinBox()
                    widget.setMinimum(param_info.get('min', -999999))
                    widget.setMaximum(param_info.get('max', 999999))
                    widget.setValue(default)
                    widget.valueChanged.connect(
                        lambda v, p=param_name: self.parameter_changed.emit(p, v)
                    )
                    param_layout.addWidget(widget)
                    
            elif param_type == float:
                widget = QDoubleSpinBox()
                widget.setMinimum(param_info.get('min', -999999.0))
                widget.setMaximum(param_info.get('max', 999999.0))
                widget.setSingleStep(param_info.get('step', 0.01))
                widget.setDecimals(4)
                widget.setValue(default)
                widget.valueChanged.connect(
                    lambda v, p=param_name: self.parameter_changed.emit(p, v)
                )
                param_layout.addWidget(widget)
                
            elif param_type == str:
                if 'options' in param_info:
                    widget = QComboBox()
                    widget.addItems(param_info['options'])
                    widget.setCurrentText(default)
                    widget.currentTextChanged.connect(
                        lambda v, p=param_name: self.parameter_changed.emit(p, v)
                    )
                else:
                    widget = QLineEdit()
                    widget.setText(default)
                    widget.textChanged.connect(
                        lambda v, p=param_name: self.parameter_changed.emit(p, v)
                    )
                param_layout.addWidget(widget)
                
            else:
                continue
                
            self.parameter_widgets[param_name] = widget
            self.params_layout.addLayout(param_layout)
            
    def _on_slider_changed(self, value: int, label: QLabel, param_name: str):
        """Handle slider value change."""
        label.setText(str(value))
        self.parameter_changed.emit(param_name, value)
        
    def _on_palette_changed(self, palette: str):
        """Handle color palette change."""
        self.parameter_changed.emit('palette', palette)
        
    def _on_invert_changed(self, state: int):
        """Handle color inversion change."""
        self.parameter_changed.emit('invert_colors', state == Qt.Checked)
        
    def _on_reset_view(self):
        """Handle reset view button."""
        self.parameter_changed.emit('reset_view', True)
        self.render_requested.emit()
        
    def _on_save_image(self):
        """Handle save image button."""
        from PyQt5.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Fractal Image", "",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)")
        
        if filename:
            self.save_requested.emit(filename)
            
    def update_status(self, message: str):
        """Update status display.
        
        Args:
            message: Status message to display
        """
        self.status_label.setText(message)
        
    def get_render_settings(self) -> dict:
        """Get current render settings.
        
        Returns:
            Dictionary of render settings
        """
        settings = {
            'progressive': self.progressive_check.isChecked(),
            'adaptive_iter': self.adaptive_check.isChecked(),
        }
        
        # Add current parameter values
        for param_name, widget in self.parameter_widgets.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                settings[param_name] = widget.value()
            elif isinstance(widget, QSlider):
                settings[param_name] = widget.value()
            elif isinstance(widget, QComboBox):
                settings[param_name] = widget.currentText()
            elif isinstance(widget, QLineEdit):
                settings[param_name] = widget.text()
                
        return settings