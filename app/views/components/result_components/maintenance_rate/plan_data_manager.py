import os
import pandas as pd

from app.analysis.output.plan_maintenance import PlanMaintenanceRate
from app.utils.week_plan_manager import WeeklyPlanManager
from app.utils.conversion import convert_value
from app.models.common.file_store import FilePaths

"""계획 데이터 관리 클래스"""    
class PlanDataManager:
    def __init__(self):
        self.plan_analyzer = PlanMaintenanceRate()
        self.current_plan = None
        self.previous_plan_path = None
        self.modified_item_keys = set()
        
    """현재 계획 설정"""
    def set_current_plan(self, data):
        if data is None or data.empty:
            return False
            
        self.current_plan = data.copy()
        self.plan_analyzer.set_current_plan(data)
        return True
        
    """이전 계획 로드"""
    def load_previous_plan(self, file_path):
        try:
            previous_df = pd.read_excel(file_path)
            
            if not previous_df.empty:
                self.previous_plan_path = file_path
                self.plan_analyzer.set_prev_plan(previous_df)
                return True, os.path.basename(file_path)
            else:
                return False, "Empty file"
        except Exception as e:
            return False, str(e)
            
    
    """
    이전 계획 설정
    FilePaths에서 이전 계획 파일 경로를 가져와서 자동 로드
    """
    def set_previous_plan(self):
        upload_plan = FilePaths.get("result_file")

        if upload_plan and os.path.exists(upload_plan):
            print(f"업로드된 이전 계획 파일 자동 로드: {upload_plan}")
            success, message = self.load_previous_plan(upload_plan)
            if success:
                return success, f"Uploaded previous plan: {message}"
            else:
                print(f"업로드된 파일 로드 실패: {message}")
                return False, f"Failed to load uploaded file: {message}"      
        else:
            # 업로드된 이전 계획 파일이 없음
            return False, "No previous plan uploaded"
        

    
    """수량 업데이트"""
    def update_quantity(self, line, time, item, new_qty):
        print(f"DataManager - 수량 업데이트 시도: line={line}, time={time}, item={item}, new_qty={new_qty}")
        if self.plan_analyzer is None:
            return False
            
        # time을 정수형으로 변환 (문자열인 경우)
        time_int = int(time) if isinstance(time, str) and time.isdigit() else time

        # Item 키 저장
        item_key = f"{line}_{time}_{item}"
        self.modified_item_keys.add(item_key)
        print(f"Item 키 추가됨: {item_key}")

        try:
            # 단순히 아이템으로만 RMC 검색
            if self.current_plan is not None and 'Item' in self.current_plan.columns and 'RMC' in self.current_plan.columns:
                # 아이템만으로 검색
                matching_rows = self.current_plan[self.current_plan['Item'] == item]
                
                if not matching_rows.empty:
                    rmc_value = matching_rows['RMC'].iloc[0]
                    if pd.notna(rmc_value) and str(rmc_value).strip():
                        # RMC 키 추가
                        rmc_key = f"{line}_{time_int}_{rmc_value}"
                        self.modified_item_keys.add(rmc_key)
                        print(f"RMC 키 추가됨: {rmc_key}")
                    else:
                        print(f"아이템 {item}의 RMC 값이 없거나 빈 값: {rmc_value}")
                else:
                    print(f"현재 계획에서 아이템을 찾을 수 없음: {item}")
        except Exception as e:
            import traceback
            print(f"RMC 키 추가 중 오류: {str(e)}")
            traceback.print_exc()

        # 현재 모든 modified_item_keys 출력
        print(f"현재 모든 변경된 키 목록: {self.modified_item_keys}")
        
        # 수량 업데이트
        return self.plan_analyzer.update_quantity(line, time, item, new_qty)
    
    """유지율 계산"""
    def calculate_maintenance_rates(self, compare_with_adjusted=True):
        print(f"calculate_maintenance_rates 호출됨, compare_with_adjusted={compare_with_adjusted}")
    
        if self.plan_analyzer is None:
            print("plan_analyzer가 None입니다")
            return None, None, None, None
        
        print(f"현재 계획: {self.current_plan is not None}")
            
        item_df, item_rate = self.plan_analyzer.calculate_items_maintenance_rate(
            compare_with_adjusted=compare_with_adjusted
        )
        
        rmc_df, rmc_rate = self.plan_analyzer.calculate_rmc_maintenance_rate(
            compare_with_adjusted=compare_with_adjusted
        )
        
        return item_df, item_rate, rmc_df, rmc_rate