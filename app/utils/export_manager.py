import os
from datetime import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from app.utils.week_plan_manager import WeeklyPlanManager

"""파일 내보내기 작업 클래스"""
class ExportManager:
    """
    데이터를 엑셀파일로 내보내는 통합 메서드
    Parameters:
            parent: 부모 위젯 (QMessageBox 표시용)
            data_df: 내보낼 데이터프레임
            start_date: 시작 날짜 (QDate 객체)
            end_date: 종료 날짜 (QDate 객체)
            is_planning: 사전할당 페이지에서 내보내기인지 여부
        
        Returns:
            성공 시 파일 경로, 실패 시 None
    """
    @staticmethod
    def export_data(parent, data_df, start_date=None, end_date=None, is_planning=False):
        try:
            if data_df is None or data_df.empty:
                QMessageBox.warning(parent, "Export Error", "No data to export")
                return None
            
            # 바탕화면 경로 가져오기
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

            # Windows에서는 '바탕 화면'일 수도 있음
            if not os.path.exists(desktop_path) and os.name == 'nt':
                # 한글 Windows의 경우
                desktop_path = os.path.join(os.path.expanduser("~"), "바탕 화면")

            # 현재 날짜 및 시간 
            now = datetime.now()
            date_str = now.strftime("%Y%m%d")
            time_str = now.strftime("%H%M%S")

            # 주차 관리자 초기화 (모든 경우에 필요)
            plan_manager = WeeklyPlanManager(output_dir=desktop_path)
            
            # 주차 정보 가져오기 (주차 폴더 생성에 사용됨)
            week_info, _, _ = plan_manager.get_week_info(start_date, end_date)
            
            # 주차별 폴더 경로 생성
            week_folder = os.path.join(desktop_path, week_info)
            
            # 폴더가 없으면 생성
            os.makedirs(week_folder, exist_ok=True)

            # 사전할당 페이지에서 호출된 경우
            if is_planning:
                # 파일명 생성
                file_name = f"LP_{date_str}_{time_str}.xlsx"
                file_path = os.path.join(week_folder, file_name)

                # 파일 저장
                data_df.to_excel(file_path, index=False)

                QMessageBox.information(
                    parent,
                    "Export Success",
                    f"File saved to desktop in {week_info} folder:\n{file_path}"
                )
                return file_path
            else:
                # 결과 페이지에서 호출한 경우
                try:
                    plan_manager = WeeklyPlanManager(output_dir=desktop_path)

                    # 조정된 계획 확인
                    export_data = data_df
                    if hasattr(parent, 'plan_maintenance_widget'):
                        adjust_plan = parent.plan_maintenance_widget.get_adjusted_plan()
                        if adjust_plan is not None:
                            export_data = adjust_plan
                            print("Saving adjusted plan.")
                        else:
                            print("No adjusted plan found. Saving current plan.")

                    # 메타데이터와 함께 저장
                    saved_path = plan_manager.save_plan_with_metadata(
                        export_data, start_date, end_date
                    )

                    print(f"Final result saved with metadata to desktop in {week_info} folder: {saved_path}")

                    # 사용자에게 성공 메시지 표시
                    QMessageBox.information(
                        parent, 
                        "Export Success", 
                        f"File saved to desktop in {week_info} folder:\n{saved_path}"
                    )

                    return saved_path

                except Exception as e:
                    print(f"Error saving metadata: {e}")
                    
                    # 오류 발생 시 기본 방식으로 저장
                    default_filename = f"Result_fallback_{date_str}_{time_str}.xlsx"
                    fallback_path = os.path.join(desktop_path, default_filename)
                    
                    data_df.to_excel(fallback_path, index=False)
                    
                    QMessageBox.information(
                        parent, 
                       "Export Success", 
                        f"File saved to desktop in {week_info} folder:\n{fallback_path}\n(No metadata)"
                    )
                    
                    return fallback_path
        except Exception as e:
            print(f"Error during export process: {str(e)}")
            QMessageBox.critical(
                parent,
                "Export Error", 
                f"An error occurred during export:\n{str(e)}"
            )
            return None
                