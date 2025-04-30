import pandas as pd
import numpy as np

class PlanMaintenanceRate:
    """
    생산 계획의 유지율을 계산하는 클래스
    원본 계획과 현재 계획 간의 유지율을 Item별, RMC별로 계산
    """
    def __init__(self):
        self.original_plan = None # 초기 계획
        self.current_plan = None # 현재 계획

    # 초기 계획 설정
    def set_original_plan(self, plan_data):
        self.original_plan = plan_data.copy()
        self.current_plan = plan_data.copy()
        return True
    
    # 수량 업데이트
    def update_quantity(self, line, time, item, new_qty, demand=None):
        """
        특정 항목의 수량 업데이트
        
        Parameters:
            line (str): 생산 라인 ID
            time (int): 시프트 번호
            item (str): 제품 코드
            new_qty (int): 새로운 수량
            
        Returns:
            bool: 업데이트 성공 여부
        """
        if self.current_plan is None:
            return False
        
        # 조건에 맞는 행 찾기
        mask = (
            (self.current_plan['Line'] == line) &
            (self.current_plan['Time'] == time) &
            (self.current_plan['Item'] == item)
        )

        # demand 조건 추가
        if demand is not None and 'Demand' in self.current_plan.columns:
            mask = mask & (self.current_plan['Demand'] == demand)

        # 수량 업데이트
        if mask.any():
            affected_rows = mask.sum()
            print(f"업데이트 할 행 수: {affected_rows}")

            self.current_plan.loc[mask, 'Qty'] = new_qty
            return True
        else:
            print(f"매칭되는 행을 찾을 수 없습니다.: {line}, {time}, {item}, Demand={demand}")
            return False
        
    
    def calculate_items_maintenance_rate(self):
        """ item별 유지율 계산 및 테이블 생성 """
        if self.original_plan is None or self.current_plan is None:
            return pd.DataFrame(), 0.0
        
        # 원본 계획 집계
        orig_grouped = self.original_plan.groupby(['Line', 'Time', 'Item'])['Qty'].sum().reset_index()

        # 수정한 계획 집계 
        curr_grouped = self.current_plan.groupby(['Line', 'Time', 'Item'])['Qty'].sum().reset_index()

        # 이전 계획과 현재 계획 병합(중복없이)
        merged = pd.merge(
            orig_grouped,
            curr_grouped,
            on=['Line', 'Time', 'Item'],
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

        # 빈 행 추가
        empty_row = {
            'Line': '', 
            'Shift': '', 
            'Item': '', 
            'pre_plan': np.nan, 
            'post_plan': np.nan, 
            'maintenance': np.nan
        }
        
        # Total 행 추가
        total_row = {
            'Line': 'Total',
            'Shift': '',
            'Item': '',
            'pre_plan': pre_plan_sum,
            'post_plan': post_plan_sum,
            'maintenance': maintenance_sum
        }

        result_df = pd.concat([result_df, pd.DataFrame([empty_row, total_row])], ignore_index=True)

        return result_df, maintenance_rate

    
    def calculate_rmc_maintenance_rate(self):
        """ rmc별 유지율 계산 """
        if self.original_plan is None or self.current_plan is None:
            return pd.DataFrame(), 0.0
        
        # 원본 계획 집계
        orig_grouped = self.original_plan.groupby(['Line', 'Time', 'RMC'])['Qty'].sum().reset_index()

        # 수정 계획 집계
        curr_grouped = self.current_plan.groupby(['Line', 'Time', 'RMC'])['Qty'].sum().reset_index()
        
        # 이전 계획과 병합
        merged = pd.merge(
            orig_grouped,
            curr_grouped,
            on=['Line', 'Time', 'RMC'],
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

        # 빈 행 추가
        empty_row = {
            'Line': '', 
            'Shift': '', 
            'RMC': '', 
            'pre_plan': np.nan, 
            'post_plan': np.nan, 
            'maintenance': np.nan
        }
        
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
        result_df = pd.concat([result_df, pd.DataFrame([empty_row, total_row])], ignore_index=True)

        return result_df, maintenance_rate
    
    
    def get_current_plan(self):
        """ 현재 데이터 반환 """
        return self.current_plan.copy() if self.current_plan is not None else None
    
    
    def reset_to_original(self):
        """ 원본 복원 """
        if self.original_plan is not None:
            self.current_plan = self.original_plan.copy()
            return True
        
        return False
    
    
    def get_changed_items(self):
        """ 수량 변경된 항목 확인 """
        if self.original_plan is None or self.current_plan is None:
            return pd.DataFrame()
        
        # 집계 후 비교
        orig_grouped = self.original_plan.groupby(['Line', 'Time', 'Item'])['Qty'].sum().reset_index()
        curr_grouped = self.current_plan.groupby(['Line', 'Time', 'Item'])['Qty'].sum().reset_index()
        
        # 병합
        merged = pd.merge(
            orig_grouped, 
            curr_grouped,
            on=['Line', 'Time', 'Item'],
            suffixes=('_orig', '_curr')
        )
        
        # 변경된 항목 필터링
        changed = merged[merged['Qty_orig'] != merged['Qty_curr']]
        return changed

    
if __name__ == "__main__":
    try:
        df = pd.read_excel('app/ssafy_result_0408.xlsx')
        # 테스트 전 원본으로 복원하여 이전 테스트의 영향 제거

        # 분석기 초기화
        analyzer = PlanMaintenanceRate()
        analyzer.set_original_plan(df)

        # 먼저 원본 상태를 확인 (선택사항)
        print("원본 상태 확인:")
        original_changed = analyzer.get_changed_items()
        print(original_changed)  # 빈 DataFrame 이어야 함

        # 수량 변경 테스트
        success1 = analyzer.update_quantity('I_01', 1, 'AB-P495W5ZJ825', 100, demand='AB-P495W5ZJ825U5')
        success2 = analyzer.update_quantity('I_01', 1, 'AB-P495W5QR295', 100, demand='AB-P495W5QR295U1')

        print(f"\n수량 변경 성공: {success1}, {success2}")

        # 변경사항 확인
        changed1 = analyzer.get_changed_items()
        print("변경항목:")
        print(changed1)

        # itme별 유지율
        item_rates_df, item_rate = analyzer.calculate_items_maintenance_rate()
        print(f"item 별 유지율: : {item_rate}")
        print(item_rates_df)

        # rmc별 유지율
        rmc_rates_df, rmc_rate = analyzer.calculate_rmc_maintenance_rate()
        print(f"\nRMC별 유지율 : {rmc_rate}")
        print(rmc_rates_df)

    except FileNotFoundError:
        print("파일을 찾을 수 없습니다.")
    except Exception as e:
        import traceback
        print(f"오류 : {e}")
        traceback.print_exc()


