import pandas as pd
import numpy as np

"""
생산 계획의 유지율을 계산하는 클래스
원본 계획과 현재 계획 간의 유지율을 Item별, RMC별로 계산

- 첫 번째 계획인 경우 이전 계획 없음 처리
- 계획 조정 시 조정 전/후 비교 기능 추가
"""
class PlanMaintenanceRate:
    def __init__(self):
        self.original_plan = None # 초기 계획
        self.current_plan = None # 현재 계획(새로 수정한 계획)
        self.adjusted_plan = None # 조정 후 계획
        self.is_first_plan = True # 첫번째 계획 여부

    """첫 번째 계획 여부를 설정"""
    def set_first_plan(self, is_first):
        # Parameters:
        #     is_first_plan (bool) : 첫 번째 계획 여부

        self.is_first_plan = is_first
        return True
    
    """초기 계획 설정"""
    def set_original_plan(self, plan_data):
        # Parameters:
        #     plan_data (DataFrame) : 생산계획 결과 데이터

        # Return:
        #     bool : 설정 성공 여부

        if plan_data is None or plan_data.empty:
            return False
        
        self.original_plan = plan_data.copy()
        self.current_plan = plan_data.copy()
        return True
    
    """새로 수정한 계획 데이터 설정"""
    def set_current_plan(self, plan_data):
        # Parameters:
        #     plan_data (DataFrame): 새 계획 데이터
            
        # Returns:
        #     bool: 설정 성공 여부
        
        if plan_data is None or plan_data.empty:
            return False
        
        self.current_plan = plan_data.copy()
        self.adjusted_plan = plan_data.copy()
        return True
    

    """특정 항목의 수량 업데이트 (계획 조정)"""
    def update_quantity(self, line, time, item, new_qty, demand=None):
        # Parameters:
        #     line (str): 생산 라인 ID
        #     time (str): 시프트 번호
        #     item (str): 제품 코드
        #     new_qty (int): 새로운 수량
        #     demand (str, optional): 수요 항목
            
        # Returns:
        #     bool: 업데이트 성공 여부
        
        if self.adjusted_plan is None:
            # 아직 조정하지 않았다면, 현재 계획으로 초기화
            if self.current_plan is not None:
                self.adjusted_plan = self.current_plan.copy()
            else:
                return False
        
        # 조건에 맞는 행 찾기
        mask = (
            (self.adjusted_plan['Line'] == line) &
            (self.adjusted_plan['Time'] == time) &
            (self.adjusted_plan['Item'] == item)
        )

        # demand 조건 추가
        if demand is not None and 'Demand' in self.adjusted_plan.columns:
            mask = mask & (self.adjusted_plan['Demand'] == demand)

        # 수량 업데이트
        if mask.any():
            affected_rows = mask.sum()
            print(f"업데이트 할 행 수: {affected_rows}")

            self.adjusted_plan.loc[mask, 'Qty'] = new_qty
            return True
        else:
            print(f"매칭되는 행을 찾을 수 없습니다.: {line}, {time}, {item}, Demand={demand}")
            return False
        
    """item별 유지율 계산 및 테이블 생성"""
    def calculate_items_maintenance_rate(self, compare_with_adjusted=False):
        # Parameters:
        #     compare_with_adjusted (bool): 조정된 계획과 비교할지 여부
            
        # Returns:
        #     tuple: (결과 DataFrame, 유지율 %)
        
        # 첫 번째 계획이고 조정되지 않았다면 계산 제외
        if self.is_first_plan and not compare_with_adjusted:
            return pd.DataFrame(), None
        
        if self.original_plan is None:
            return pd.DataFrame(), None
        
        # 비교 대상 결정
        if compare_with_adjusted:
            # 조정 결과와 비료
            if self.adjusted_plan is None:
                return pd.DataFrame(), None
            comparison_plan = self.adjusted_plan
        else:
            # 현재 계획과 비교
            if self.current_plan is None:
                return pd.DataFrame(), None
            comparison_plan = self.current_plan
        
        # 원본 계획 집계
        orig_grouped = self.original_plan.groupby(['Line', 'Time', 'Item'])['Qty'].sum().reset_index()

        # 비교할 계획 집계 
        curr_grouped = comparison_plan.groupby(['Line', 'Time', 'Item'])['Qty'].sum().reset_index()

        # 이전 계획과 비교 계획 병합(중복없이)
        merged = pd.merge(
            orig_grouped,
            curr_grouped,
            on=['Line', 'Time', 'Item'],
            how='outer', # 외부 병합으로 모든 항목 포함
            suffixes=('_orig', '_curr')
        )

        # 유지 수량 계산
        merged['maintenance'] = merged.apply(lambda x: min(x['Qty_orig'], x['Qty_curr']), axis=1)

        # 필드명 수정
        result_df = merged.rename(columns={
            'Line': 'Line',
            'Time': 'Shift',
            'Item': 'Item',
            'Qty_orig': 'pre_plan',
            'Qty_curr': 'post_plan'
        })

        # 합계 계산
        pre_plan_sum = result_df['pre_plan'].sum()
        post_plan_sum = result_df['post_plan'].sum()
        maintenance_sum = result_df['maintenance'].sum()

        # 유지율 계산
        maintenance_rate = (maintenance_sum / pre_plan_sum) * 100 if pre_plan_sum > 0 else 0
        
        # Total 행 추가
        total_row = {
            'Line': 'Total',
            'Shift': '',
            'Item': '',
            'pre_plan': pre_plan_sum,
            'post_plan': post_plan_sum,
            'maintenance': maintenance_sum
        }

        result_df = pd.concat([result_df, pd.DataFrame([total_row])], ignore_index=True)

        return result_df, maintenance_rate

    """RMC별 유지율 계산"""
    def calculate_rmc_maintenance_rate(self, compare_with_adjusted=False):
        # Parameters:
        #     compare_with_adjusted (bool): 조정된 계획과 비교할지 여부
            
        # Returns:
        #     tuple: (결과 DataFrame, 유지율 %)

        # 첫 번째 수행이고 조정된 계획과의 비교가 아니면 유지율 계산 제외
        if self.is_first_plan and not compare_with_adjusted:
            return pd.DataFrame(), None
            
        if self.original_plan is None:
            return pd.DataFrame(), None
            
        # 비교 대상 결정
        if compare_with_adjusted:
            # 조정된 계획과 비교
            if self.adjusted_plan is None:
                return pd.DataFrame(), None
            comparison_plan = self.adjusted_plan
        else:
            # 현재 계획과 비교
            if self.current_plan is None:
                return pd.DataFrame(), None
            comparison_plan = self.current_plan
        
        # 원본 계획 집계
        orig_grouped = self.original_plan.groupby(['Line', 'Time', 'RMC'])['Qty'].sum().reset_index()

        # 수정 계획 집계
        curr_grouped = comparison_plan.groupby(['Line', 'Time', 'RMC'])['Qty'].sum().reset_index()
        
        # 이전 계획과 병합
        merged = pd.merge(
            orig_grouped,
            curr_grouped,
            on=['Line', 'Time', 'RMC'],
            how='outer',
            suffixes=('_orig', '_curr')
        )

        # 유지 수량 계산
        merged['maintenance'] = merged.apply(lambda x: min(x['Qty_orig'], x['Qty_curr']), axis=1)

        result_df = merged.rename(columns={
            'Line': 'Line',
            'Time': 'Shift',
            'RMC': 'RMC',
            'Qty_orig': 'pre_plan',
            'Qty_curr': 'post_plan'
        })
       
        # 합계
        pre_plan_sum = result_df['pre_plan'].sum()
        post_plan_sum = result_df['post_plan'].sum()
        maintenance_sum = result_df['maintenance'].sum()

        # RMC별 유지율 계산
        maintenance_rate = (maintenance_sum / pre_plan_sum) * 100 if pre_plan_sum > 0 else 0

        # Total 행 추가
        total_row = {
            'Line': 'Total',
            'Shift': '',
            'RMC': '',
            'pre_plan': pre_plan_sum,
            'post_plan': post_plan_sum,
            'maintenance': maintenance_sum
        }

        # 결과에 추가
        result_df = pd.concat([result_df, pd.DataFrame([total_row])], ignore_index=True)

        return result_df, maintenance_rate
    
    
    """ 현재 데이터 반환 """
    def get_current_plan(self):
        return self.current_plan.copy() if self.current_plan is not None else None
    
    """조정된 계획 데이터 반환"""
    def get_adjusted_plan(self):
        return self.adjusted_plan.copy() if self.adjusted_plan is not None else None
    
    """ 원본 복원 """
    def reset_to_original(self):
        if self.original_plan is not None:
            self.current_plan = self.original_plan.copy()
            self.adjusted_plan = self.original_plan.copy()
            return True
        
        return False
    
    """조정 사항 초기화 (현재 계획으로 복원)"""
    def reset_adjustments(self):
        if self.current_plan is not None:
            self.adjusted_plan = self.current_plan.copy()
            return True
        
        return False
    
    """수량 변경된 항목 확인"""
    def get_changed_items(self, compare_with_adjusted=False):        
        # Parameters:
        #     compare_with_adjusted (bool): 조정된 계획과 비교할지 여부
        
        # Returns:
        #     DataFrame: 변경된 항목 목록
        
        if self.original_plan is None:
            return pd.DataFrame()
        
        # 비교 대상 결정
        if compare_with_adjusted:
            if self.adjusted_plan is None:
                return pd.DataFrame()
            comparison_plan = self.adjusted_plan
        else:
            if self.current_plan is None:
                return pd.DataFrame()
            comparison_plan = self.current_plan
        
        # 집계 후 비교
        orig_grouped = self.original_plan.groupby(['Line', 'Time', 'Item'])['Qty'].sum().reset_index()
        curr_grouped = comparison_plan.groupby(['Line', 'Time', 'Item'])['Qty'].sum().reset_index()
        
        # 병합
        merged = pd.merge(
            orig_grouped, 
            curr_grouped,
            on=['Line', 'Time', 'Item'],
            how='outer',
            suffixes=('_orig', '_curr')
        )
        
        # 변경된 항목 필터링
        changed = merged[merged['Qty_orig'] != merged['Qty_curr']]
        return changed
        
    
if __name__ == "__main__":
    try:
        # 파일 로드 (예시)
        df_prev = pd.read_excel('app/ssafy_result_0408.xlsx')
        df_current = pd.read_excel('app/ssafy_result_0408.xlsx')
        
        # 분석기 초기화
        analyzer = PlanMaintenanceRate()

        # 첫 번째 계획 여부
        is_first_plan = True
        analyzer.set_first_plan(is_first_plan)

        # 2. 이전 계획 설정
        analyzer.set_original_plan(df_prev)
        
        # 3. 현재 계획 설정
        analyzer.set_current_plan(df_current)

        # 4. 계획 조정 예시 (필요 시)
        #analyzer.update_quantity('I_01', 1, 'AB-P495W5ZJ825', 100, demand='AB-P495W5ZJ825U5')
        #analyzer.update_quantity('I_01', 1, 'AB-P495W5QR295', 100, demand='AB-P495W5QR295U1')
        
        # 예시: 현재 계획과 이전 계획 비교 (조정 전)
        if not is_first_plan:
            print("현재 계획과 이전 계획의 비교 (조정 전):")
            
            # item별 유지율
            item_rates_df, item_rate = analyzer.calculate_items_maintenance_rate(compare_with_adjusted=False)
            if item_rate is not None:
                print(f"item 별 유지율: {item_rate:.2f}%")
                print(item_rates_df)
            
            # RMC별 유지율
            rmc_rates_df, rmc_rate = analyzer.calculate_rmc_maintenance_rate(compare_with_adjusted=False)
            if rmc_rate is not None:
                print(f"RMC별 유지율: {rmc_rate:.2f}%")
                print(rmc_rates_df)
        
        # 예시: 조정된 계획과 이전 계획 비교 (조정 후)
        print("\n조정된 계획과 이전 계획의 비교 (조정 후):")
        
        # item별 유지율 (조정 후)
        #item_rates_adj_df, item_rate_adj = analyzer.calculate_items_maintenance_rate(compare_with_adjusted=True)
        #if item_rate_adj is not None:
        #    print(f"item 별 유지율 (조정 후): {item_rate_adj:.2f}%")
        #    print(item_rates_adj_df)
        
        # RMC별 유지율 (조정 후)
        #rmc_rates_adj_df, rmc_rate_adj = analyzer.calculate_rmc_maintenance_rate(compare_with_adjusted=True)
        #if rmc_rate_adj is not None:
        #    print(f"RMC별 유지율 (조정 후): {rmc_rate_adj:.2f}%")
        #    print(rmc_rates_adj_df)
        
        # 변경된 항목 확인
        #if not is_first_plan:
        #    changed_items = analyzer.get_changed_items(compare_with_adjusted=True)
        #    print("\n변경된 항목:")
        #    print(changed_items)

    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")
    except Exception as e:
        import traceback
        print(f"오류 : {e}")
        traceback.print_exc()
