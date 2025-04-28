from PyQt5.QtWidgets import QTabWidget
from app.views.components.visualization.tab_implementations import UtilizationTab, ProductionTab, DefectRateTab, ShiftComparisonTab, ProductDistributionTab, TimeSeriesTab, TimeSeriesTab

# Main tabs widget that holds all visualization tabs
class AnalysisTabsWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabPosition(QTabWidget.North)
        self.setTabShape(QTabWidget.Rounded)
        
        # Initialize tabs
        self.init_tabs()
        
    def init_tabs(self):
        """Initialize all visualization tabs"""
        # Add Utilization tab
        utilization_tab = UtilizationTab(self)
        self.addTab(utilization_tab, "Utilization")
        
        # Add Production tab
        production_tab = ProductionTab(self)
        self.addTab(production_tab, "Production")
        
        # Add Defect Rate tab
        defect_rate_tab = DefectRateTab(self)
        self.addTab(defect_rate_tab, "Defect Rate")
        
        # Add Shift Comparison tab
        shift_comparison_tab = ShiftComparisonTab(self)
        self.addTab(shift_comparison_tab, "Shift Comparison")
        
        # Add Product Distribution tab
        product_distribution_tab = ProductDistributionTab(self)
        self.addTab(product_distribution_tab, "Product Distribution")
        
        # Add Time Series tab
        time_series_tab = TimeSeriesTab(self)
        self.addTab(time_series_tab, "Time Series")
        
        # Add Heatmap tab
        heatmap_tab = TimeSeriesTab(self)
        self.addTab(heatmap_tab, "Heatmap")
    
    def refresh_all_data(self):
        """Refresh data in all tabs"""
        for i in range(self.count()):
            tab = self.widget(i)
            if hasattr(tab, 'refresh_data'):
                tab.refresh_data()

