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


"""DataInputPage의 Run 버튼에 주차 정보 활용 계획 저장 기능 추가"""
def enhance_run_botton_handler(data_input_page):
    # Parameters:
    #     data_input_page: DataInputPage 인스턴스

    # 원래 Run 버튼 클릭 핸들러를 저장
    original_handler = data_input_page.on_run_clicked

    def enhanced_run_handler():
        """확장된 Run 버튼 핸들러"""
        # 기존 Run 핸들러 호출
        original_handler()
        
        # 파일과 날짜 범위가 제대로 선택되었는지 확인
        file_paths = data_input_page.get_file_paths()
        
        if not file_paths:
            QMessageBox.warning(data_input_page, "경고", "파일을 선택해주세요.")
            return
        
        try:
            # 입력 데이터 처리 (이 함수는 실제 프로젝트에 맞게 구현되어야 함)
            plan_df = process_input_data(file_paths)
            
            # 주차 정보를 활용한 계획 처리
            saved_path = process_plan_with_date_range(data_input_page, plan_df)
            
            # 저장 성공 메시지 표시
            QMessageBox.information(
                data_input_page, 
                "성공", 
                f"계획이 성공적으로 저장되었습니다:\n{saved_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                data_input_page, 
                "오류", 
                f"계획 처리 중 오류가 발생했습니다:\n{str(e)}"
            )
    
    # 기존 핸들러를 향상된 핸들러로 교체
    data_input_page.on_run_clicked = enhanced_run_handler