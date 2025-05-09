import os
import pandas as pd

from app.analysis.output.plan_maintenance import PlanMaintenanceRate
from app.utils.week_plan_manager import WeeklyPlanManager

"""계획 데이터 관리 클래스"""    
class PlanDataManager:
    def __init__(self):
        self.plan_analyzer = PlanMaintenanceRate()
        self.current_plan = None
        self.previous_plan_path = None
        self.is_first_plan = True
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
            previous_df = pd.read_excel(file_path, sheet_name='result')
            
            if not previous_df.empty:
                self.previous_plan_path = file_path
                self.is_first_plan = False
                self.plan_analyzer.set_first_plan(False)
                self.plan_analyzer.set_prev_plan(previous_df)
                return True, os.path.basename(file_path)
            else:
                return False, "Empty file"
        except Exception as e:
            return False, str(e)
    
    """이전 계획 자동 탐색"""
    def detect_previous_plan(self, start_date, end_date):
        if start_date is None or end_date is None:
            return False, "No date information"
            
        try:
            plan_manager = WeeklyPlanManager()
            is_first_plan, previous_plan_path, message = plan_manager.detect_previous_plan(
                start_date, end_date
            )
            
            self.is_first_plan = is_first_plan
            self.previous_plan_path = previous_plan_path
            self.plan_analyzer.set_first_plan(is_first_plan)
            
            if not is_first_plan and previous_plan_path and os.path.exists(previous_plan_path):
                success, message = self.load_previous_plan(previous_plan_path)
                return success, message
            else:
                # 첫 번째 계획인 경우 현재 계획을 이전 계획으로 설정
                if self.current_plan is not None:
                    self.plan_analyzer.set_prev_plan(self.current_plan)
                return False, message
        except Exception as e:
            return False, str(e)
    
    """수량 업데이트"""
    def update_quantity(self, line, time, item, new_qty, demand=None):
        if self.plan_analyzer is None:
            return False
            
        # 아이템 키
        item_key = f"{line}_{time}_{item}_{demand}"
        self.modified_item_keys.add(item_key)
        
        # 수량 업데이트
        return self.plan_analyzer.update_quantity(line, time, item, new_qty, demand)
    
    """유지율 계산"""
    def calculate_maintenance_rates(self, compare_with_adjusted=True):
        print(f"calculate_maintenance_rates 호출됨, compare_with_adjusted={compare_with_adjusted}")
    
        if self.plan_analyzer is None:
            print("plan_analyzer가 None입니다")
            return None, None, None, None
        
        print(f"현재 계획: {self.current_plan is not None}")
        print(f"첫 번째 계획 여부: {self.is_first_plan}")
            
        item_df, item_rate = self.plan_analyzer.calculate_items_maintenance_rate(
            compare_with_adjusted=compare_with_adjusted
        )
        
        rmc_df, rmc_rate = self.plan_analyzer.calculate_rmc_maintenance_rate(
            compare_with_adjusted=compare_with_adjusted
        )
        
        return item_df, item_rate, rmc_df, rmc_rate