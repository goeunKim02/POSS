from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from app.views.components.visualization.mpl_canvas import MplCanvas
from app.views.components.visualization.visualization_updater import VisualizationUpdater


class CapaTab(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_page = parent
        self.capa_canvas = None
        self.util_canvas = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.no_data_message = QLabel("Please load the data")
        self.no_data_message.setAlignment(Qt.AlignCenter)
        self.no_data_message.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            background-color: transparent;
            border: none;
        """)

        layout.addWidget(self.no_data_message)
        
        # Capa 차트 캔버스
        self.capa_canvas = MplCanvas(width=4, height=5, dpi=100)
        layout.addWidget(self.capa_canvas)
        
        # Utilization 차트 캔버스
        self.util_canvas = MplCanvas(width=5, height=5, dpi=100)
        layout.addWidget(self.util_canvas)

        self.capa_canvas.hide()
        self.util_canvas.hide()
    
    """
    콘텐츠 업데이트
    """
    def update_content(self, capa_data, utilization_data):
        if capa_data is not None and utilization_data is not None:
            self.no_data_message.hide()
            self.capa_canvas.show()
            self.util_canvas.show()
            VisualizationUpdater.update_capa_chart(self.capa_canvas, capa_data)
            VisualizationUpdater.update_utilization_chart(self.util_canvas, utilization_data)
    
    """
    캔버스들 반환
    """
    def get_canvases(self):
        return [self.capa_canvas, self.util_canvas]