from app.views.components.visualization.visualizaiton_manager import VisualizationManager

"""output 시각화 업데이트 클래스"""
class VisualizationUpdater:

    """Capa 비율 차트 업데이트"""
    @staticmethod
    def update_capa_chart(canvas, capa_ratio_data):
        if capa_ratio_data and len(capa_ratio_data) > 0:
            VisualizationManager.create_chart(
                capa_ratio_data,
                chart_type='bar',
                title='Plant Capacity Ratio',
                xlabel='Plant',
                ylabel='Ratio (%)',
                ax=canvas.axes
            )
        else:
            canvas.axes.text(0.5, 0.5, 'Please load data', ha='center', va='center', fontsize=18)
        
        canvas.draw()

    """요일별 가동률 차트 업데이트"""
    @staticmethod
    def update_utilization_chart(canvas, utilization_data):
        canvas.axes.clear()
        
        if utilization_data:
            days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            sorted_data = {day: utilization_data.get(day, 0) for day in days_order}
            
            VisualizationManager.create_chart(
                sorted_data,
                chart_type='bar',
                title='Daily Utilization Rate',
                xlabel='Day of week',
                ylabel='Utilization Rate(%)',
                ax=canvas.axes,
                ylim=(0, 100),
                threshold_values=[60, 80],
                threshold_colors=['#4CAF50', '#FFC107', '#F44336'],
                value_fontsize=14
            )
        else:
            canvas.axes.text(0.5, 0.5, 'No utilization data available', ha='center', va='center', fontsize=18)
        
        canvas.draw()
    
    """출하포트 Capa 차트 업데이트"""
    @staticmethod
    def update_port_capa_chart(canvas, port_capa_data):
        canvas.axes.clear()
        
        if port_capa_data and len(port_capa_data) > 0:
            VisualizationManager.create_chart(
                port_capa_data,
                chart_type='bar', 
                title='Port Capacity Utilization',
                xlabel='Port',
                ylabel='Utilization (%)',
                ax=canvas.axes
            )
        else:
            canvas.axes.text(0.5, 0.5, 'Please load data', ha='center', va='center', fontsize=18)
        
        canvas.draw()