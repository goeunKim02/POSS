from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from app.views.components.visualization.visualization_tabs import AnalysisTabsWidget

class AnalysisPage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        
        # Add header if needed
        header_label = QLabel("Production Analysis")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Add analysis tabs widget
        self.analysis_tabs = AnalysisTabsWidget(self)
        layout.addWidget(self.analysis_tabs)
        
    def refresh_all_data(self):
        """Refresh all visualizations"""
        if hasattr(self, 'analysis_tabs'):
            self.analysis_tabs.refresh_all_data()




