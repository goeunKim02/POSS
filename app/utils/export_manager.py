import os
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox
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
            
            # 바탕화면 경로
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

            # 한글 Windows의 경우
            if not os.path.exists(desktop_path) and os.name == 'nt':
                desktop_path = os.path.join(os.path.expanduser("~"), "바탕 화면")

            now = datetime.now()
            date_str = now.strftime("%Y%m%d")
            time_str = now.strftime("%H%M%S")
            plan_manager = WeeklyPlanManager(output_dir=desktop_path)
            
            week_info, _, _ = plan_manager.get_week_info(start_date, end_date)
            
            week_folder = os.path.join(desktop_path, week_info)
            
            os.makedirs(week_folder, exist_ok=True)

            # 사전할당 페이지에서 호출된 경우
            if is_planning:
                file_name = f"LP_{date_str}_{time_str}.xlsx"
                file_path = os.path.join(week_folder, file_name)

                data_df.to_excel(file_path, index=False)

                QMessageBox.information(
                    parent,
                    "Export Success",
                    f"File saved to desktop in {week_info} folder:\n{file_path}"
                )
                return file_path
            else:
                try:
                    plan_manager = WeeklyPlanManager(output_dir=desktop_path)

                    export_data = data_df

                    if hasattr(parent, 'plan_maintenance_widget'):
                        adjust_plan = parent.plan_maintenance_widget.get_adjusted_plan()

                        if adjust_plan is not None:
                            export_data = adjust_plan
                        else:
                            print("No adjusted plan found. Saving current plan.")

                    saved_path = plan_manager.save_plan_with_metadata(
                        export_data, start_date, end_date
                    )

                    QMessageBox.information(
                        parent, 
                        "Export Success", 
                        f"File saved to desktop in {week_info} folder:\n{saved_path}"
                    )

                    return saved_path

                except Exception as e:
                    print(f"Error saving metadata: {e}")
                    
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
                