import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from app.models.common.fileStore import FilePaths, DataStore

def analyze_and_get_results(use_flexible_matching=True, result_data=None):
    # 원본 분석 함수 호출
    return analyze_shipment_performance(use_flexible_matching, result_data)

"""
Result 파일을을 사용하여 당주 출하 실패 건과 만족률을 계산합니다.
출하 가능 조건 (두 가지 모두 충족해야 함):
1) Result엑셀에서 Time <= Due_LT (Due_LT가 Time을 넘어야 함)
2) 같은 Item+Tosite_group 조합의 Due_LT 내 생산량이 필요한 SOP 이상이어야 함
"""
def analyze_shipment_performance(use_flexible_matching=True, result_data=None):
    
    def normalize_key(item, site):
        """키를 정규화하여 일관된 비교가 가능하도록 합니다"""
        return (str(item).strip(), '' if pd.isna(site) else str(site).strip())
    
    def extract_fields_from_item(item_str):
        """Item 문자열에서 Project, Basic2, Tosite_group, RMC, Color 추출"""
        result = {
            "Project": "",
            "Basic2": "",
            "Tosite_group": "",
            "RMC": "",
            "Color": ""
        }
        
        try:
            if isinstance(item_str, str) and len(item_str) > 7:
                # 인덱스가 유효한 범위 내에 있는지 확인하면서 추출
                if len(item_str) > 3:
                    result["Project"] = item_str[3:7]
                    result["RMC"] = item_str[3:-3] if len(item_str) > 6 else ""
                if len(item_str) > 7:
                    result["Basic2"] = item_str[3:8]
                    result["Tosite_group"] = item_str[7:8]
                if len(item_str) > 8 and len(item_str) > 11:
                    result["Color"] = item_str[8:-4]
        except:
            pass
            
        return result
        
    try:
        # 1. 결과 데이터 로드
        if result_data is not None:
            # 직접 전달된 데이터 사용
            result_df = result_data.copy()
        else:
            # DataStore에서 확인
            result_df = DataStore.get("result_data")
            if result_df is not None:
                print("DataStore에서 결과 데이터를 로드했습니다.")
            else:
                # 파일에서 로드
                result_file = FilePaths.get("result_file")
                if result_file and os.path.exists(result_file):
                    try:
                        # 모든 시트 확인
                        xl = pd.ExcelFile(result_file)
                        sheets = xl.sheet_names
                        if len(sheets) > 0:
                            result_df = pd.read_excel(result_file, sheet_name=sheets[0])  # 첫 번째 시트 사용
                    except Exception as e:
                        print(f"결과 파일 로드 오류: {str(e)}")
                        return None, None, None
                        
        # 결과 데이터가 없으면 종료
        if result_df is None:
            print("결과 데이터를 로드할 수 없습니다.")
            return None, None, None
            
        # 데이터 타입 변환
        result_df['Due_LT'] = pd.to_numeric(result_df['Due_LT'], errors='coerce').fillna(0).astype(int)
        result_df['Time'] = pd.to_numeric(result_df['Time'], errors='coerce').fillna(0).astype(int)
        result_df['Qty'] = pd.to_numeric(result_df['Qty'], errors='coerce').fillna(0).astype(int)
        
        # SOP 컬럼 확인 - Result 파일 내에 SOP 컬럼이 있다고 가정
        if 'SOP' not in result_df.columns:
            print("결과 데이터에 'SOP' 컬럼이 없습니다. 'Qty' 컬럼을 SOP로 사용합니다.")
            # SOP 컬럼이 없는 경우, Qty를 기준으로 SOP 계산 (Item+Tosite_group별 합계)
            # Item과 Tosite_group 추출 
            for i, row in result_df.iterrows():
                fields = extract_fields_from_item(row['Item'])
                for field_name, field_value in fields.items():
                    result_df.loc[i, field_name] = field_value
            
            # Item+Tosite_group 별로 그룹화하여 Qty 합계 계산 -> 이를 SOP로 가정
            grouped = result_df.groupby(['Item', 'Tosite_group'])['Qty'].sum().reset_index()
            grouped.rename(columns={'Qty': 'SOP'}, inplace=True)
            
            # 원본 데이터프레임에 SOP 정보 병합
            result_df = pd.merge(
                result_df, 
                grouped[['Item', 'Tosite_group', 'SOP']], 
                on=['Item', 'Tosite_group'], 
                how='left'
            )
        else:
            # SOP 컬럼이 있는 경우 숫자로 변환
            result_df['SOP'] = pd.to_numeric(result_df['SOP'], errors='coerce').fillna(0).astype(int)
            
            # Item과 Tosite_group 추출
            for i, row in result_df.iterrows():
                fields = extract_fields_from_item(row['Item'])
                for field_name, field_value in fields.items():
                    result_df.loc[i, field_name] = field_value

        # Due_LT 컬럼 확인 및 추가
        if 'Due_LT' not in result_df.columns:
            raise ValueError("분석 실패: 결과 데이터에 'Due_LT' 컬럼이 없습니다.")
            
        # Item+Tosite_group 별로 SOP 맵 생성 (일관성을 위해 기존 코드 구조 유지)
        demand_sop_map = {}
        item_to_sites = {}
        
        # 각 결과 행을 순회하며 SOP 정보 추출
        for _, row in result_df.iterrows():
            item = str(row['Item']).strip()
            to_site = str(row['Tosite_group']).strip() 
            sop = row['SOP']
            
            # 정규화된 키 사용
            key = normalize_key(item, to_site)
            
            # SOP 맵 업데이트 (중복 키가 있을 경우 가장 큰 값 사용)
            if key in demand_sop_map:
                demand_sop_map[key] = max(demand_sop_map[key], sop)
            else:
                demand_sop_map[key] = sop
                
            # Item별 Tosite_group 목록 저장 (유연한 매칭에 사용)
            item_part = key[0]
            if item_part not in item_to_sites:
                item_to_sites[item_part] = {}
                
            # 해당 Item의 모든 Tosite_group에 대한 SOP 저장
            item_to_sites[item_part][key[1]] = sop  # 여기서는 각각의 SOP를 저장
        
        # 여기가 중요한 변경 부분 - 각 Item+Tosite_group 별 Due_LT 내 생산량 계산
        # Time > Due_LT 인 경우에는 출하 적합성 판단에서 제외되지만, SOP 계산에는 포함
        exact_match_qty = {}
        
        for key in demand_sop_map.keys():
            norm_item, norm_site = key
            
            # 정확한 매칭: Item과 Tosite_group이 모두 일치하는 행 찾기
            matching_rows = result_df[
                (result_df['Item'].apply(lambda x: normalize_key(x, '')[0] == norm_item)) & 
                (result_df['Tosite_group'].apply(lambda x: normalize_key('', x)[1] == norm_site))
            ]
            
            # 모든 행의 총 생산량 (전체 SOP 계산용)
            total_qty = matching_rows['Qty'].sum()
            
            # Due_LT 내의 생산량만 집계 (출하 가능 여부 판단용)
            due_lt_qty = sum(row['Qty'] for _, row in matching_rows.iterrows() 
                         if row['Time'] <= row['Due_LT'])
            
            exact_match_qty[key] = {
                'total_qty': total_qty,       # 전체 생산량 (SOP 계산용)
                'due_lt_qty': due_lt_qty      # Due_LT 내 생산량 (출하 가능 여부 판단용)
            }
        
        # 각 레코드 별로 개별 분석
        result_analysis = []
        
        # 모델 단위로 처리 (Item+Tosite_group 조합)
        model_records = {}  # 각 모델별 레코드 인덱스 저장
        
        # 각 레코드별 분석
        for idx, row in result_df.iterrows():
            item = str(row['Item']).strip()
            to_site = str(row['Tosite_group']).strip()
            
            norm_key = normalize_key(item, to_site)
            
            qty = row['Qty']
            time = row['Time']
            due_lt = row['Due_LT']
            sop = row['SOP']
            
            # Demand 맵에 있는지 확인 (Item+Tosite_group 조합)
            in_demand = norm_key in demand_sop_map
            demand_sop = demand_sop_map.get(norm_key, 0)
            
            # 조건 1: 시간 조건 - Time이 Due_LT 이하인지
            time_condition_met = time <= due_lt
            
            # 조건 2: 수량 조건 - Item과 Tosite_group 조합의 Due_LT 내 생산량이 SOP 이상인지
            match_info = exact_match_qty.get(norm_key, {'due_lt_qty': 0, 'total_qty': 0})
            due_lt_qty = match_info['due_lt_qty']
            total_qty = match_info['total_qty']
            
            qty_condition_met = due_lt_qty >= demand_sop
            
            # 두 조건 모두 만족해야 출하 가능
            is_shippable = in_demand and time_condition_met and qty_condition_met
            
            # 모델 단위 처리를 위한 레코드 저장
            if norm_key not in model_records:
                model_records[norm_key] = []
            model_records[norm_key].append(idx)
            
            # 결과 저장
            result_analysis.append({
                'Index': idx,
                'Item': item,
                'Tosite_group': to_site,
                'To_site': to_site,  # 호환성을 위해 To_site 컬럼 추가
                'NormalizedKey': norm_key,
                'MatchKey': norm_key,
                'MatchType': "exact",
                'Line': row.get('Line', ''),
                'Time': time,
                'Due_LT': due_lt,
                'Qty': qty,
                'DemandSOP': demand_sop,
                'TotalQty': total_qty,       # 전체 생산량
                'QualifiedQty': due_lt_qty,  # Due_LT 내 생산량
                'InDemand': in_demand,
                'TimeConditionMet': time_condition_met,
                'QtyConditionMet': qty_condition_met,
                'IsShippable': is_shippable
            })
        
        # 분석 결과를 데이터프레임으로 변환
        analysis_df = pd.DataFrame(result_analysis)
        
        # 결과 데이터프레임에 출하 상태 및 실패 이유 추가
        result_df['IsShippable'] = [item['IsShippable'] for item in result_analysis]
        result_df['ShipmentStatus'] = result_df['IsShippable'].apply(
            lambda x: "출하가능" if x else "출하실패"
        )
        result_df['MatchType'] = [item['MatchType'] for item in result_analysis]
        result_df['To_site'] = result_df['Tosite_group']  # 호환성을 위해 To_site 컬럼 추가
        
        # 실패 이유 추가
        result_df['FailureReason'] = ''
        for idx, row in analysis_df.iterrows():
            if not row['IsShippable']:
                if not row['InDemand']:
                    result_df.at[row['Index'], 'FailureReason'] = 'Not in Demand'
                elif not row['TimeConditionMet'] and not row['QtyConditionMet']:
                    result_df.at[row['Index'], 'FailureReason'] = 'Time>Due_LT & Qty<SOP'
                elif not row['TimeConditionMet']:
                    result_df.at[row['Index'], 'FailureReason'] = 'Time>Due_LT'
                elif not row['QtyConditionMet']:
                    result_df.at[row['Index'], 'FailureReason'] = 'Qty<SOP'
        
        # 출하 불가능 아이템 필터링
        unshippable_items = analysis_df[~analysis_df['IsShippable']]
        
        # 모델 기준 통계 계산
        model_stats = {}
        
        # 먼저 SOP 맵에 있는 모든 모델에 대해 기본 통계 초기화
        for key, sop in demand_sop_map.items():
            model_stats[key] = {
                'total_records': 0,
                'success_records': 0,
                'sop': sop,
                'total_qty': 0,          # 모든 생산량
                'due_lt_qty': 0,         # Due_LT 내 생산량 
                'success_qty': 0,        # 출하 성공 판정된 생산량
                'match_type': 'exact'    # 기본값
            }
        
        # Result에서 각 레코드를 해당 모델의 통계에 반영
        for idx, row in analysis_df.iterrows():
            key = row['NormalizedKey']
            
            if key in model_stats:  # SOP 맵에 있는 모델인 경우만 처리
                model_stats[key]['total_records'] += 1
                model_stats[key]['total_qty'] += row['Qty']
                
                # Due_LT 내 생산량 추가
                if row['TimeConditionMet']:
                    model_stats[key]['due_lt_qty'] += row['Qty']
                
                # 출하 성공 판정된 생산량 추가
                if row['IsShippable']:
                    model_stats[key]['success_records'] += 1
                    model_stats[key]['success_qty'] += row['Qty']
        
        # 당주 출하 만족률(수량 기준) 계산
        # 전체: SOP 합계
        total_sop = sum(demand_sop_map.values())
        
        # 성공: 출하 성공 판단된 아이템의 QTY
        success_qty = sum(stats['success_qty'] for stats in model_stats.values())
        
        # Due_LT 내 총 생산량
        due_lt_total_qty = sum(stats['due_lt_qty'] for stats in model_stats.values())
        
        # 전체 생산량 (Time>Due_LT 포함)
        total_produced_qty = sum(stats['total_qty'] for stats in model_stats.values())
        
        # 수량 기준 성공률
        qty_success_rate = success_qty / total_sop * 100 if total_sop > 0 else 0
        
        # 당주 출하 만족률(모델 기준) 계산
        # 전체 모델 수 (Item+Tosite_group 조합 수)
        total_models = len(demand_sop_map)
        
        # 성공 모델 수 (하나라도 출하 성공인 모델)
        success_models = sum(1 for stats in model_stats.values() if stats['success_records'] > 0)
        
        model_success_rate = success_models / total_models * 100 if total_models > 0 else 0
        
        # 통계 요약
        summary = {
            'total_sop': total_sop,
            'success_qty': success_qty,
            'due_lt_total_qty': due_lt_total_qty,
            'total_produced_qty': total_produced_qty,
            'qty_success_rate': qty_success_rate,
            'total_models': total_models,
            'success_models': success_models,
            'model_success_rate': model_success_rate,
            'exact_match_count': len(analysis_df),
            'flexible_match_count': 0,
            'no_match_count': 0,
            'model_stats': model_stats  # 모델별 상세 통계
        }
        
        # 결과 출력
        print("\n===== 당주 출하 만족률 분석 결과 =====")
        print(f"Item+Tosite_group 조합 수: {total_models}")
        print(f"전체 SOP 수량: {total_sop:.0f}")
        print(f"Due_LT 내 생산량: {due_lt_total_qty:.0f}")
        print(f"전체 생산량(Time>Due_LT 포함): {total_produced_qty:.0f}")
        print(f"출하 성공 수량(QTY): {success_qty:.0f}")
        print(f"당주 출하 만족률(수량 기준): {qty_success_rate:.2f}%")
        print(f"성공 모델 수: {success_models}")
        print(f"실패 모델 수: {total_models - success_models}")
        print(f"전체 모델 수: {total_models}")
        print(f"모델 기준 성공률: {model_success_rate:.2f}%")
        
        # 출하 실패 항목 표시
        demand_failures = unshippable_items[unshippable_items['InDemand']]
        if len(demand_failures) > 0:
            # 실패 이유 분석
            time_condition_fail = len(demand_failures[~demand_failures['TimeConditionMet']])
            qty_condition_fail = len(demand_failures[~demand_failures['QtyConditionMet']])
            both_condition_fail = len(demand_failures[~demand_failures['TimeConditionMet'] & ~demand_failures['QtyConditionMet']])
            
            print(f"\n실패 원인 분석:")
            print(f"- Time > Due_LT 조건 위반: {time_condition_fail}건")
            print(f"- 생산량 < SOP 조건 위반: {qty_condition_fail}건") 
            print(f"- 두 조건 모두 위반: {both_condition_fail}건")
        else:
            print("출하 실패 항목이 없습니다.")
        
        return result_df, summary, analysis_df
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()  # 상세 오류 정보 출력
        return None, None, None