import pandas as pd
import numpy as np
from app.models.common.fileStore import FilePaths
from app.utils.fileHandler import load_file
import os
import traceback

class CapaUtilization:
    """요일별 가동률 계산 함수"""
    @staticmethod
    def analyze_utilization(data_df):
        # Args:
        #     data_df (DataFrame): 최적화 결과 데이터프레임
            
        # Returns:
        #     dict: 요일별 가동률 데이터 {'Mon': 75.5, 'Tue': 82.3, ...}
        try:
            # 입력 데이터 검증
            if data_df is None or data_df.empty:
                print("최적화 결과 데이터가 비어 있습니다.")
                return {day: 0 for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}

            # 데이터 복사본 생성
            df_demand = data_df.copy()
            
            # 마스터 파일에서 생산능력 데이터(capa_qty) 로드
            master_file = FilePaths.get("master_excel_file")
            if not master_file:
                print("마스터 파일 경로가 설정되지 않았습니다.")
                return {day: 0 for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}

            try:
                sheets = load_file(master_file, sheet_name="capa_qty")

                if isinstance(sheets, dict):
                    df_capa_qty = sheets.get('capa_qty', pd.DataFrame())
                else:
                    df_capa_qty = sheets
                
                if df_capa_qty.empty:
                    print("capa_qty 데이터가 비어 있습니다.")
                    return {day: 0 for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}
                
            except Exception as e:
                print(f"생산능력 데이터 로드 중 오류 발생: {str(e)}")
                return {day: 0 for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}
            
                
            # 근무를 요일에 매핑
            shift_to_day = {
                1: 'Mon', 2: 'Mon',
                3: 'Tue', 4: 'Tue',
                5: 'Wed', 6: 'Wed',
                7: 'Thu', 8: 'Thu',
                9: 'Fri', 10: 'Fri',
                11: 'Sat', 12: 'Sat',
                13: 'Sun', 14: 'Sun',
            }

            # 일별 생산능력 계산
            day_capacity = {}
            for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
                day_shifts = [shift for shift, d in shift_to_day.items() if d == day]
                day_total_capacity = 0

                for shift in day_shifts:
                    shift_capacity = 0

                    # 각 제조동별 처리
                    for factory in ['I', 'D', 'K', 'M']:
                        # 해당 공장 라인들 가져오기
                        factory_lines = df_capa_qty[df_capa_qty['Line'].str.startswith(f'{factory}_')].index.tolist()
                    
                        if not factory_lines or shift not in df_capa_qty.columns:
                            continue

                        # 최대 라인 제약 확인
                        max_line_key = f'Max_line_{factory}'

                        # 제약이 없는 경우 전체 라인 수 사용
                        max_line = df_capa_qty.loc[max_line_key, shift] if max_line_key in df_capa_qty.index and pd.notna(df_capa_qty.loc[max_line_key, shift]) else len(factory_lines)

                        # 각 라인의 생산 능력 가져오기
                        line_capacities = [(line, df_capa_qty.loc[line, shift]) for line in factory_lines if pd.notna(df_capa_qty.loc[line, shift])]
                        line_capacities.sort(key=lambda x:x[1], reverse=True)  # Sort by capacity in descending order
                        
                        # 최대 수량 제약 확인
                        max_qty_key = f'Max_qty_{factory}'
                        max_qty = df_capa_qty.loc[max_qty_key, shift] if max_qty_key in df_capa_qty.index and pd.notna(df_capa_qty.loc[max_qty_key, shift]) else float('inf')

                        # 라인 수와 최대 수량 간의 더 제한적인 제약 적용
                        factory_capacity = 0
                        for i, (line, capacity) in enumerate(line_capacities):
                            if i < max_line and factory_capacity + capacity <= max_qty:
                                factory_capacity += capacity
                            elif i < max_line and factory_capacity < max_qty:
                                factory_capacity = max_qty # Max qty constraint reached
                                break
                        
                        shift_capacity += factory_capacity

                    day_total_capacity += shift_capacity
                
                day_capacity[day] = day_total_capacity
            
            # 수요 수량에 기반한 일별 생산량 계산
            df_demand['Day'] = df_demand['Time'].map(shift_to_day)
            day_production = df_demand.groupby('Day')['Qty'].sum()

            # 일별 가동률 계산
            utilization_rate = {}
            for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
                if day in day_capacity and day_capacity[day] > 0:
                    if day in day_production:
                        utilization_rate[day] = (day_production[day] / day_capacity[day]) * 100
                    else:
                        utilization_rate[day] = 0
                else:
                    utilization_rate[day] = 0 if day_capacity[day] == 0 else None

            print("daily utilization rate(%):")
            for day, rate in utilization_rate.items():
                if rate is not None:
                    print(f"{day}: {rate:.2f}%")
                else:
                    print(f"{day}: No capacity availble")

            return utilization_rate
        
        except Exception as e:
                print(f"가동률 계산 중 오류 발생: {str(e)}")
                traceback.print_exc()
                # 빈 결과 반환
                return {day: 0 for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}


    """셀 이동 시 요일별 가동률 업데이트"""  
    @staticmethod
    def update_utilization_for_cell_move(data_df, item_data, new_data, is_initial=False):
        # Args:
        #     data_df (DataFrame): 기존 데이터프레임
        #     item_data (dict): 이동 전 아이템 데이터
        #     new_data (dict): 이동 후 아이템 데이터
        #     is_initial (초기 분석 여부 (True: 출력 안함))
            
        # Returns:
        #     dict: 업데이트된 가동률 데이터
       
        try:
            # 아이템 정보 찾기
            item_id = item_data.get('Item')
            
            if item_id is not None:
                print(f"업데이트 전 Qty 합계: {data_df['Qty'].sum()}")
                print(f"업데이트 대상 아이템: {item_id}")
                print(f"대상 라인/시프트: {item_data.get('Line')}/{item_data.get('Time')}")

                # 해당 아이템 행 찾기
                item_row = data_df[data_df['Item'] == item_id]
                
                if not item_row.empty:
                    # 인덱스 가져오기
                    idx = item_row.index[0]
                    
                    # 라인 정보 업데이트
                    if 'Line' in new_data:
                        data_df.at[idx, 'Line'] = new_data['Line']
                        
                    # 근무 정보 업데이트
                    if 'Time' in new_data:
                        data_df.at[idx, 'Time'] = int(new_data['Time'])
                        
                    # 수량 정보 업데이트
                    if 'Qty' in new_data:
                        data_df.at[idx, 'Qty'] = int(float(new_data['Qty']))
                        
            # 업데이트된 데이터로 가동률 분석
            return CapaUtilization.analyze_utilization(data_df)
            
        except Exception as e:
            print(f"셀 이동 시 가동률 업데이트 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            return {day: 0 for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}


