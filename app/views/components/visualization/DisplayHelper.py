from app.views.components.visualization.visualizaiton_manager import VisualizationManager

"""시각화 헬퍼 클래스"""
class DisplayHelper:
    """차트를 표시하거나 데이터가 없으면 메세지 표시"""
    @staticmethod
    def show_chart_or_message(canvas, data, chart_config):
        # Args:
        #     canvas: Matplotlib 캔버스 객체
        #     data: 차트 데이터 (딕셔너리 또는 DataFrame)
        #     chart_config: 차트 설정 딕셔너리
        #         - has_data_check: 데이터 유효성 확인 함수
        #         - chart_type: 차트 유형 ('bar', 'line' 등)
        #         - title: 차트 제목
        #         - xlabel: X축 레이블
        #         - ylabel: Y축 레이블
        #         - transform_data: 데이터 변환 함수 
        #         - extra_params: 추가 차트 파라미터

        # 캔버스 초기화
        canvas.axes.clear()

        # 비교 데이터 감지
        is_comparison_data = (
            isinstance(data, dict) and
            'original' in data and
            'adjusted' in data
        )

        # 비교 차트 타입인데 데이터가 비교 형식이 아니면 차트 타입 변경
        chart_type = chart_config.get('chart_type', 'bar')
        if chart_type == 'comparison_bar' and not is_comparison_data:
            chart_type = 'bar'

        # 일반 데이터인데 비교 데이터 형식이면 차트 타입 변경
        if chart_type != 'comparison_bar' and is_comparison_data:
            chart_type = 'comparison_bar'

        # 차트 설정 업데이트
        chart_config['chart_type'] = chart_type

        # 데이터 유효성 확인
        has_data_func = chart_config.get('has_data_check', lambda x:x is not None and len(x) > 0)

        print(f"차트 타입 (처리 전): {chart_config.get('chart_type')}")
        print(f"비교 데이터 여부: {is_comparison_data}")
        print(f"차트 타입 (처리 후): {chart_type}")

        # 비교 차트 데이터의 유효성 확인
        if is_comparison_data:
            has_data = (
                has_data_func(data['original']) or
                has_data_func(data['adjusted'])
            )
        else:
            has_data = has_data_func(data)

        # 데이터가 있으면 차트 표시
        if has_data:
            canvas.axes.set_axis_on() # 축 보이기
            canvas.axes.set_frame_on(True)
            canvas.axes.get_xaxis().set_visible(True)
            canvas.axes.get_yaxis().set_visible(True)

            display_data = data
            if 'transform_data' in chart_config and chart_config['transform_data']:
                display_data = chart_config['transform_data'](data)


            # 기본 파라미터 설정
            chart_params = {
                'chart_type': chart_type,
                'title': chart_config['title'],
                'xlabel': chart_config['xlabel'],
                'ylabel': chart_config['ylabel'],
                'ax': canvas.axes
            }
            
            # 추가 파라미터 병합
            if 'extra_params' in chart_config:
                chart_params.update(chart_config['extra_params'])
                
            # 차트 생성
            VisualizationManager.create_chart(display_data, **chart_params)

        else:
            # 데이터가 없으면 메세지 표시
            canvas.axes.text(0.5, 0.5, "Please Load to Data", ha="center", va="center", fontsize=20)
            canvas.axes.set_frame_on(False)
            canvas.axes.get_xaxis().set_visible(False)
            canvas.axes.get_yaxis().set_visible(False)
        
        # 캔버스 갱신
        canvas.draw()
