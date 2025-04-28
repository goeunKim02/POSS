from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from app.views.components.visualization.mpl_canvas import MplCanvas

# Bae class for visualization tabs
class VisualizationTab(QWidget):
    def __init__(self, partent=None):
        super().__init__(partent)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        
        # Controls layout
        self.controls_layout = QHBoxLayout()
        self.setup_controls(self.controls_layout)
        layout.addLayout(self.controls_layout)
        
        # Canvas for chart
        self.canvas = MplCanvas()
        layout.addWidget(self.canvas)
        
        # Initial update
        self.update_chart()

    def setup_controls(self, layout):
        """Setup control widgets - override in subclasses"""
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addStretch(1)
        layout.addWidget(refresh_btn)

    def update_chart(self):
        """Update the chart - override in subclasses"""
        pass

    def refresh_data(self):
        """Refresh data and update chart"""
        self.update_chart()

