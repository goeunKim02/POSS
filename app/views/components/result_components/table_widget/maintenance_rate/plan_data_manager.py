import os
import pandas as pd

from app.analysis.output.plan_maintenance import PlanMaintenanceRate
from app.utils.conversion import convert_value
from app.models.common.file_store import FilePaths
from app.utils.item_key import ItemKeyManager

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
            
        # 원래 값 확인
        original_qty = self.get_original_quantity(line, time, item)
        original_qty = int(original_qty) if original_qty is not None else None
        new_qty = int(new_qty) if new_qty is not None else None

        # ItemKeyManager를 사용하여 아이템 키 생성
        item_key = ItemKeyManager.get_item_key(line, time, item)

        # 값이 원래대로 돌아갔는지 확인
        if original_qty == new_qty and original_qty is not None:
            # 수정된 아이템 목록에서 제거
            if item_key in self.modified_item_keys:
                self.modified_item_keys.remove(item_key)
                print(f"값이 원래대로 돌아와 Item 키 제거됨: {item_key}")
        else:
            # 값이 변경된 경우 - 수정된 목록에 추가
            self.modified_item_keys.add(item_key)
            print(f"Item 키 추가됨: {item_key}")

        try:
            # 아이템으로 RMC 검색
             if self.current_plan is not None and all(col in self.current_plan.columns for col in ['Item', 'Line', 'Time', 'RMC']):
                # ItemKeyManager의 create_mask_for_item 함수 사용
                mask = ItemKeyManager.create_mask_for_item(self.current_plan, line, time, item)

                matching_rows = self.current_plan[mask]
                
                if not matching_rows.empty:
                    rmc_value = matching_rows['RMC'].iloc[0]
                    if pd.notna(rmc_value) and str(rmc_value).strip():
                        # RMC 키 생성
                        rmc_key = ItemKeyManager.get_item_key(line, time, rmc_value)
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
            
        # 항상 조정된 계획을 사용 (compare_with_adjusted=True)
        # 이렇게 하면 사용자 조정이 즉시 반영됨
        item_df, item_rate = self.plan_analyzer.calculate_items_maintenance_rate(
            compare_with_adjusted=True  # 항상 adjusted_plan 사용
        )
        
        rmc_df, rmc_rate = self.plan_analyzer.calculate_rmc_maintenance_rate(
            compare_with_adjusted=True  # 항상 adjusted_plan 사용
        )
        
        return item_df, item_rate, rmc_df, rmc_rate
    

    def get_original_quantity(self, line, time, item):
        """원래 수량 가져오기"""
        if not hasattr(self, 'plan_analyzer') or not self.plan_analyzer:
            return None
            
        if not hasattr(self.plan_analyzer, 'prev_plan') or self.plan_analyzer.prev_plan is None:
            return None
        
        # 원래 계획에서 해당 아이템 찾기
        try:
            prev_plan = self.plan_analyzer.prev_plan
            mask = (
                (prev_plan['Line'].astype(str) == str(line)) & 
                (prev_plan['Time'].astype(int) == int(time)) & 
                (prev_plan['Item'] == item)
            )
            
            if mask.any():
                return prev_plan[mask].iloc[0].get('Qty')
            else:
                print(f"원래 계획에서 아이템을 찾을 수 없음: {line}, {time}, {item}")
        except Exception as e:
            print(f"원래 수량 조회 중 오류: {str(e)}")
        
        return None