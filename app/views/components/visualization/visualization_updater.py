from app.views.components.visualization.visualizaiton_manager import VisualizationManager
from app.views.components.visualization.DisplayHelper import DisplayHelper

"""output 시각화 업데이트 클래스"""
class VisualizationUpdater:
    """Capa 차트의 데이터 유효성 확인 함수"""
    @staticmethod
    def _is_capa_data_valid(data):
        return data and len(data) > 0
    
    """Utilization 차트의 데이터 유효성 확인 함수"""
    @staticmethod
    def _is_utilization_data_valid(data):
        return data and any(value > 0 for value in data.values())
    
    """요일 데이터 정렬 함수"""
    @staticmethod
    def _transform_utilization_data(data):
        days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
        # 요일 순서대로 데이터 정렬
        sorted_data = {}
        for day in days_order:
            sorted_data[day] = data.get(day, 0)
        return sorted_data

    """Capa 비율 차트 업데이트"""
    @staticmethod
    def update_capa_chart(canvas, capa_ratio_data):
        chart_config = {
            'has_data_check': VisualizationUpdater._is_capa_data_valid,
            'chart_type' :'bar',
            'title' : 'Plant Capacity Ratio',
            'xlabel' :'Plant',
            'ylabel' :'Ratio (%)'
        }
        DisplayHelper.show_chart_or_message(canvas, capa_ratio_data, chart_config)

    """요일별 가동률 차트 업데이트"""
    @staticmethod
    def update_utilization_chart(canvas, utilization_data):
        chart_config = {
            'has_data_check': VisualizationUpdater._is_utilization_data_valid,
            'chart_type': 'bar',
            'title' :'Daily Utilization Rate',
            'xlabel' : 'Day of week',
            'ylabel' : 'Utilization Rate(%)',
            'transform_data': VisualizationUpdater._transform_utilization_data,
            'extra_params': {
                'ylim': (0, 110),
                'threshold_values': [60, 80],
                'threshold_colors': ['#4CAF50', '#FFC107', '#F44336'],
                'value_fontsize': 14
            }
        }
        DisplayHelper.show_chart_or_message(canvas, utilization_data, chart_config)

    """출하포트 Capa 차트 업데이트"""
    @staticmethod
    def update_port_capa_chart(canvas, port_capa_data):
        chart_config = {
            'chart_type' :'bar', 
            'title' :'Port Capacity Utilization',
            'xlabel' :'Port',
            'ylabel' :'Utilization (%)',
        }
    