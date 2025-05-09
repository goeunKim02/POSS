from app.views.components.visualization.visualizaiton_manager import VisualizationManager
from app.views.components.visualization.DisplayHelper import DisplayHelper
from app.analysis.output.material_shortage_analysis import MaterialShortageAnalyzer

"""output 시각화 업데이트 클래스"""
class VisualizationUpdater:
    """Capa 차트의 데이터 유효성 확인 함수"""
    @staticmethod
    def _is_capa_data_valid(data):
        if isinstance(data, dict) and 'original' in data and 'adjusted' in data:
            return data['original'] and len(data['original']) > 0
        return data and len(data) > 0
    
    """Utilization 차트의 데이터 유효성 확인 함수"""
    @staticmethod
    def _is_utilization_data_valid(data):
        if isinstance(data, dict) and 'original' in data and 'adjusted' in data:
            return data['original'] and any(value > 0 for value in data['original'].values())
        return data and any(value > 0 for value in data.values())
    
    """요일 데이터 정렬 함수"""
    @staticmethod
    def _transform_utilization_data(data):
        days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        if isinstance(data, dict) and 'original' in data and 'adjusted' in data:
            # 비교 데이터가 있는 경우
            sorted_original = {}
            sorted_adjusted = {}

            for day in days_order:
                sorted_original[day] = data['original'].get(day, 0)
                sorted_adjusted[day] = data['adjusted'].get(day, 0)

            return {'original':sorted_original, 'adjusted': sorted_adjusted}
        else:
            # 단일 데이터인 경우
            sorted_data = {}
            for day in days_order:
                sorted_data[day] = data.get(day, 0)
            return sorted_data

    """Capa 비율 차트 업데이트"""
    @staticmethod
    def update_capa_chart(canvas, capa_ratio_data):
        # 비교 데이터형식 감지
        is_comparison = isinstance(capa_ratio_data, dict) and 'original' in capa_ratio_data and 'adjusted' in capa_ratio_data
        
        chart_config = {
            'has_data_check' : VisualizationUpdater._is_capa_data_valid,
            'chart_type' : 'comparison_bar' if is_comparison else 'bar',
            'title' : 'Plan Capacity Ratio Comparison' if is_comparison else 'Plant Capacity Ratio',
            'xlabel' :'Plant',
            'ylabel' :'Ratio (%)',
            'transform_data': None,
            'extra_params': {
                'show_value': True,
                'value_fontsize': 14,
                'show_legend': is_comparison,
                'ylim': None  # 자동 계산
            }
        }
     
        DisplayHelper.show_chart_or_message(canvas, capa_ratio_data, chart_config)

    """요일별 가동률 차트 업데이트"""
    @staticmethod
    def update_utilization_chart(canvas, utilization_data):
         # 비교 데이터 형식 감지
        is_comparison = isinstance(utilization_data, dict) and 'original' in utilization_data and 'adjusted' in utilization_data
        
        chart_config = {
            'has_data_check': VisualizationUpdater._is_utilization_data_valid,
            'chart_type': 'comparison_bar' if is_comparison else 'bar',
            'title': 'Daily Utilization Rate Comparison' if is_comparison else 'Daily Utilization Rate',
            'xlabel': 'Day of week',
            'ylabel': 'Utilization Rate(%)',
            'transform_data': VisualizationUpdater._transform_utilization_data,
            'extra_params': {
                'ylim': (0, 110), 
                'threshold_values': [60, 80],
                'threshold_colors': ['#4CAF50', '#FFC107', '#F44336'],
                'threshold_labels': ['Good', 'Warning', 'High'] if is_comparison else ['', '', ''],
                'show_value': True,
                'value_fontsize': 14,
                'show_legend': is_comparison
            }
        }
       
        DisplayHelper.show_chart_or_message(canvas, utilization_data, chart_config)

    """출하포트 Capa 차트 업데이트"""
    @staticmethod
    def update_port_capa_chart(canvas, port_capa_data):
        pass
        # # 비교 데이터 형식 감지
        # is_comparison = isinstance(port_capa_data, dict) and 'original' in port_capa_data and 'adjusted' in port_capa_data
        
        # chart_config = {
        #     'has_data_check': VisualizationUpdater._is_capa_data_valid,
        #     'chart_type': 'comparison_bar' if is_comparison else 'bar',
        #     'title': 'Port Capacity Utilization Comparison' if is_comparison else 'Port Capacity Utilization',
        #     'xlabel': 'Port',
        #     'ylabel': 'Utilization (%)',
        #     'transform_data': None,
        #     'extra_params': {
        #         'show_value': True,
        #         'value_fontsize': 14,
        #         'show_legend': is_comparison
        #     }
        # }
        
        # DisplayHelper.show_chart_or_message(canvas, port_capa_data, chart_config)


    """자재 부족량 차트 업데이트"""
    @staticmethod
    def update_material_shortage_chart(canvas, result_data=None):
        # 자재 부족량 분석 실행 (결과 데이터 직접 전달)
        analyzer = MaterialShortageAnalyzer()
        analyzer.analyze_material_shortage(result_data)
        
        # 차트 데이터 가져오기
        shortage_data = analyzer.get_shortage_chart_data()
            
        # 데이터가 없는 경우 메시지 표시
        if not shortage_data:
            canvas.axes.clear()
            canvas.axes.text(0.5, 0.5, "No Material Shortage Found", 
                        ha="center", va="center", fontsize=20)
            canvas.axes.set_frame_on(False)
            canvas.axes.get_xaxis().set_visible(False)
            canvas.axes.get_yaxis().set_visible(False)
            canvas.draw()
            return analyzer
    

        # 차트 설정
        chart_config = {
            'has_data_check': VisualizationUpdater._is_material_shortage_data_valid,
            'chart_type': 'bar',
            'title': 'Material Shortage Analysis',
            'xlabel': 'Model',
            'ylabel': 'Shortage (%)',
            'extra_params': {
                'threshold_values': [20, 50],
                'threshold_colors': ['#FFD6D6', '#FFAAAA', '#FF7777'],  # 연한 빨강 → 진한 빨강
                'value_fontsize': 14,
                'max_bars': 20,  # 최대 표시 항목 수
                'sort_descending': True,  # 내림차순 정렬
                'truncate_labels': False,  # 긴 레이블 축약
                'label_max_length': 20,  # 레이블 최대 길이
                'annotate_above_bars': True  # 막대 위에 값 표시
            }
        }
        
        DisplayHelper.show_chart_or_message(canvas, shortage_data, chart_config)
        
        
        return analyzer  # 추가 정보 표시를 위해 분석기 객체 반환
    
    """Material 차트의 데이터 유효성 확인 함수"""
    @staticmethod
    def _is_material_shortage_data_valid(data):
        return data and len(data) > 0
    
