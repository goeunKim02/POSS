from PyQt5.QtWidgets import QMessageBox
from app.utils.week_plan_manager import WeeklyPlanManager

"""DataInputPage에서 선택한 날짜 범위를 이용하여 결과 파일 처리"""
def process_plan_with_date_range(parent_widget, plan_df):
    # Parameters:
    #     parent_widget: DataInputPage 인스턴스
    #     plan_df (DataFrame): 계획 데이터
        
    # Returns:
    #     str: 저장된 파일 경로

    # 선택한 날짜 범위 가져오기
    start_date, end_date = parent_widget.date_selector.get_date_range()

    # 계획 관리자 초기화
    plan_manager = WeeklyPlanManager()

    # 이전 계획 감지
    is_first_plan, previous_plan_path, message = plan_manager.detect_previous_plan(
        start_date, end_date
    )

    # 계획 저장
    saved_path = plan_manager.save_plan_with_metadate(
        plan_df, start_date, end_date, previous_plan_path
    )

    return saved_path
