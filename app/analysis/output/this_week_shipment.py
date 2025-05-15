import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from app.models.common.file_store import FilePaths, DataStore

"""
당주 출하 분석을 수행하는 함수의 래퍼

Args:
    use_flexible_matching (bool): 유연한 매칭 사용 여부 (True이면 Item+To_Site 일치에 실패해도 Item만 일치하면 대체 To_Site 매칭 시도)
    result_data (DataFrame): 직접 전달된 결과 데이터
    
Returns:
    tuple: (결과 데이터프레임, 요약 통계, 분석 데이터프레임)
"""
def analyze_and_get_results(use_flexible_matching=True, result_data=None):

    # 원본 분석 함수 호출
    return analyze_shipment_performance(use_flexible_matching, result_data)

"""
Demand 파일과 Result 파일을 분석하여 당주 출하 실패 건과 만족률을 계산합니다.

출하 가능 조건 (두 가지 모두 충족해야 함):
1) Result엑셀에서 Time <= Due_LT (Due_LT가 Time을 넘어야 함)
2) Result엑셀에서 Item과 to_site가 일치하는 값들의 QTY총합이 Demand엑셀의 demand 시트에서의 Item과 to_site가 일치하는 값들의 SOP보다 크거나 같아야함

Args:
    use_flexible_matching (bool): True이면 Item+To_Site 일치에 실패해도 Item만 일치하면 대체 To_Site 매칭 시도
    result_data (DataFrame): 직접 전달된 결과 데이터

Returns:
    tuple: (결과 데이터프레임, 통계 요약 딕셔너리, 분석 결과 데이터프레임)
"""
def analyze_shipment_performance(use_flexible_matching=True, result_data=None):
    
    def normalize_key(item, site):
        """키를 정규화하여 일관된 비교가 가능하도록 합니다"""
        return (str(item).strip(), '' if pd.isna(site) else str(site).strip())
        
    try:
        # 데이터 로드 로직 수정 - 파일 경로 대신 DataStore 또는 인자로 전달된 데이터 사용
        
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
        
        # 2. 수요 데이터 로드
        demand_df = DataStore.get("demand_data")
        if demand_df is not None:
            print("DataStore에서 수요 데이터를 로드했습니다.")
        else:
            # 파일에서 로드
            demand_file = FilePaths.get("demand_excel_file")
            if demand_file and os.path.exists(demand_file):
                try:
                    # 시트 확인
                    xl = pd.ExcelFile(demand_file)
                    if 'demand' in xl.sheet_names:
                        demand_df = pd.read_excel(demand_file, sheet_name='demand')
                    else:
                        # 첫 번째 시트 사용
                        demand_df = pd.read_excel(demand_file, sheet_name=0)
                        print(f"{demand_file}의 첫 번째 시트에서 수요 데이터를 로드했습니다.")
                except Exception as e:
                    print(f"수요 파일 로드 오류: {str(e)}")
            else:
                print("수요 파일을 찾을 수 없습니다다")

                
        # 결과 및 수요 데이터가 없으면 종료
        if result_df is None:
            print("결과 데이터를 로드할 수 없습니다.")
            return None, None, None
            
        if demand_df is None:
            print("수요 데이터를 로드할 수 없습니다.")
            # 더미 수요 데이터를 다시 생성
            if demand_df is None:
                return None, None, None
        
        # 데이터 로드 후 분석 시작
        # print(f"결과 데이터 레코드 수: {len(result_df)}")
        # print(f"수요 데이터 레코드 수: {len(demand_df)}")
        
        # 디버깅: 두 데이터프레임의 모든 컬럼 이름 출력
        # print("결과 데이터프레임 컬럼:", result_df.columns.tolist())
        # print("수요 데이터프레임 컬럼:", demand_df.columns.tolist())

        # 데이터 타입 변환
        result_df['Due_LT'] = pd.to_numeric(result_df['Due_LT'], errors='coerce').fillna(0).astype(int)
        result_df['Time'] = pd.to_numeric(result_df['Time'], errors='coerce').fillna(0).astype(int)
        result_df['Qty'] = pd.to_numeric(result_df['Qty'], errors='coerce').fillna(0).astype(int)
        demand_df['SOP'] = pd.to_numeric(demand_df['SOP'], errors='coerce').fillna(0).astype(int)

        # 컬럼명 대소문자 통일
        # 'To_Site'와 'To_site'의 대소문자 차이 해결을 위해 일관된 네이밍 사용
        if 'To_Site' in result_df.columns:
            result_df = result_df.rename(columns={'To_Site': 'To_site'})
        elif 'TO_SITE' in result_df.columns:
            result_df = result_df.rename(columns={'TO_SITE': 'To_site'})
        
        # Due_LT 컬럼 확인 및 추가
        if 'Due_LT' not in result_df.columns:
            raise ValueError("분석 실패: 결과 데이터에 'Due_LT' 컬럼이 없습니다.")
        
        # SOP가 양수인 수요만 필터링
        positive_sop_demand = demand_df[demand_df['SOP'] >= 0]
        # print(f"SOP가 양수인 수요 레코드 수: {len(positive_sop_demand)}")
        
        # 디버깅: Demand 파일의 처음 5개 레코드 출력하여 구조 확인
        # print("\nDemand 파일의 처음 5개 레코드:")
        # print(positive_sop_demand.head())
        
        # Demand 파일의 demand 시트에서 Item과 To_Site 조합에 대한 SOP 맵 생성
        demand_sop_map = {}
        
        # Item별 To_Site 목록 맵 (유연한 매칭에 사용)
        item_to_sites = {}
        
        # Demand 파일의 To_Site 컬럼명 확인
        to_site_column = None
        for col in ['To_Site', 'To_site', 'TO_SITE']:
            if col in demand_df.columns:
                to_site_column = col
                break
        
        if to_site_column is None:
            # print("경고: Demand 파일에서 To_Site 컬럼을 찾을 수 없습니다!")
            # print("사용 가능한 컬럼:", demand_df.columns.tolist())
            # 가장 가능성 있는 컬럼 추측
            possible_cols = [col for col in demand_df.columns if 'site' in col.lower() or 'to' in col.lower()]
            if possible_cols:
                to_site_column = possible_cols[0]
                # print(f"'{to_site_column}' 컬럼을 To_Site로 사용합니다.")
            else:
                # To_site 컬럼이 없으면 더미 컬럼 추가
                demand_df['To_site'] = 'Unknown'
                to_site_column = 'To_site'
                # print("Demand 파일에 To_Site 컬럼이 없어 'Unknown' 값으로 새 컬럼을 추가했습니다.")
        
        # Item 컬럼 확인
        item_column = 'Item' if 'Item' in demand_df.columns else None
        if item_column is None:
            # 가장 가능성 있는 컬럼 추측
            possible_cols = [col for col in demand_df.columns if 'item' in col.lower()]
            if possible_cols:
                item_column = possible_cols[0]
                # print(f"'{item_column}' 컬럼을 Item으로 사용합니다.")
            else:
                # print("Demand 파일에 Item 컬럼이 없습니다. 분석을 진행할 수 없습니다.")
                return None, None, None
        
        # 모든 값을 문자열로 변환하고 공백 제거
        for _, row in positive_sop_demand.iterrows():
            to_site = str(row[to_site_column]).strip()
            item = str(row[item_column]).strip()
            
            # 정규화된 키 사용
            key = normalize_key(item, to_site)
            
            # 디버깅을 위해 몇 개의 키 출력
            # if _ < 5:  # 처음 5개만 출력
                # print(f"키 생성: Item='{item}', To_Site='{to_site}' -> 정규화 키: {key}")
                
            if key in demand_sop_map:
                # 같은 Item+To_Site 조합이 여러 개 있을 경우 SOP 합산
                demand_sop_map[key] += row['SOP']
            else:
                demand_sop_map[key] = row['SOP']
            
            # Item별 To_Site 목록 저장 (유연한 매칭에 사용)
            item_part = key[0]
            if item_part not in item_to_sites:
                item_to_sites[item_part] = {}
            
            # 해당 Item의 모든 To_Site에 대한 SOP 저장
            item_to_sites[item_part][key[1]] = demand_sop_map[key]
        
        # print(f"SOP가 있는 Item+To_Site 조합 수: {len(demand_sop_map)}")
        
        # 결과 데이터프레임의 To_site 컬럼명 확인
        to_site_result_column = None
        for col in ['To_site', 'To_Site', 'TO_SITE']:
            if col in result_df.columns:
                to_site_result_column = col
                break
        
        if to_site_result_column is None:
            # print("경고: 결과 파일에서 To_site 컬럼을 찾을 수 없습니다!")
            # print("사용 가능한 컬럼:", result_df.columns.tolist())
            # 가장 가능성 있는 컬럼 추측
            possible_cols = [col for col in result_df.columns if 'site' in col.lower() or 'to' in col.lower()]
            if possible_cols:
                to_site_result_column = possible_cols[0]
                # print(f"'{to_site_result_column}' 컬럼을 To_site로 사용합니다.")
                result_df = result_df.rename(columns={to_site_result_column: 'To_site'})
                to_site_result_column = 'To_site'
            else:
                # To_site 컬럼이 없으면 더미 컬럼 추가
                result_df['To_site'] = 'Unknown'
                to_site_result_column = 'To_site'
                # print("결과 파일에 To_site 컬럼이 없어 'Unknown' 값으로 새 컬럼을 추가했습니다.")
        else:
            # 표준화된 이름으로 변경
            if to_site_result_column != 'To_site':
                result_df = result_df.rename(columns={to_site_result_column: 'To_site'})
                to_site_result_column = 'To_site'
        
        # 디버깅: 첫 5개 demand_sop_map 항목 출력
        # print("\nDemand SOP 맵 (처음 5개):")
        # for i, (key, value) in enumerate(list(demand_sop_map.items())[:5]):
        #     print(f"{i+1}. 키: {key}, SOP: {value}")
        
        # 디버깅: Item별 To_Site 목록 출력 (유연한 매칭에 사용)
        # print("\nItem별 가능한 To_Site 목록 (처음 5개):")
        # for i, (item, sites) in enumerate(list(item_to_sites.items())[:5]):
        #     print(f"{i+1}. Item: {item}, 가능한 To_Sites: {list(sites.keys())}")
        
        # 각 레코드를 분석하기 전에 먼저 Item+To_site 별 총 생산량(QTY) 계산
        # 정확한 매칭과 유연한 매칭 둘 다 계산
        exact_match_qty = {}
        flexible_match_qty = {}
        
        for key in demand_sop_map.keys():
            norm_item, norm_site = key
            
            # 정확한 매칭: Item과 To_site가 모두 일치하는 행 찾기
            matching_rows = result_df[
                result_df['Item'].apply(lambda x: normalize_key(x, '')[0] == norm_item) & 
                result_df['To_site'].apply(lambda x: normalize_key('', x)[1] == norm_site)
            ]
            
            # if len(matching_rows) > 0:
                # print(f"Item='{norm_item}', To_site='{norm_site}'에 대한 일치하는 행 수: {len(matching_rows)}")
            
            # Due_LT 내의 생산량만 집계
            qualified_qty = sum(row['Qty'] for _, row in matching_rows.iterrows() 
                            if row['Time'] <= row['Due_LT'])
            exact_match_qty[key] = qualified_qty
        
        # 유연한 매칭: Item만 일치하는 경우, 각 To_site별로 집계
        if use_flexible_matching:
            for item, sites in item_to_sites.items():
                for site in sites:
                    # 이 Item+To_site 조합과 정확히 일치하는 행 찾기
                    exact_rows = result_df[
                        (result_df['Item'].apply(lambda x: normalize_key(x, '')[0] == item)) &
                        (result_df['To_site'].apply(lambda x: normalize_key('', x)[1] == site))
                    ]
                    
                    # Due_LT 내의 생산량 계산
                    site_qty = sum(row['Qty'] for _, row in exact_rows.iterrows() 
                                  if row['Time'] <= row['Due_LT'])
                    
                    # 각 Item+To_site 조합별로 생산량 저장
                    flexible_match_qty[(item, site)] = site_qty
                    
                    # 정확한 매칭에서 계산한 수량보다 다를 경우 로그 출력
                    if (item, site) in exact_match_qty and exact_match_qty[(item, site)] != site_qty:
                        print(f"주의: Item='{item}', To_site='{site}'의 생산량 계산 불일치")
                        print(f"  - 정확한 매칭: {exact_match_qty[(item, site)]}")
                        print(f"  - 유연한 매칭: {site_qty}")
        
        # 각 레코드 별로 개별 분석
        result_analysis = []
        
        # 모델 단위로 처리 (Item+To_site 조합)
        model_records = {}  # 각 모델별 레코드 인덱스 저장
        
        # 각 레코드별 분석
        for idx, row in result_df.iterrows():
            item = str(row['Item']).strip()
            
            # To_site가 NaN인 경우 처리
            orig_to_site = row['To_site']
            if pd.isna(orig_to_site):
                # 해당 Item에 대한. 가능한 To_site 찾기
                item_norm = normalize_key(item, '')[0]
                if item_norm in item_to_sites and len(item_to_sites[item_norm]) > 0:
                    # SOP가 가장 큰 To_site 선택
                    best_site = max(item_to_sites[item_norm].items(), key=lambda x: x[1])[0]
                    to_site = best_site
                    # print(f"Item '{item}'의 To_site가 NaN이므로 Demand에서 가장 높은 SOP를 가진 To_site '{best_site}'로 대체")
                else:
                    to_site = ''
            else:
                to_site = str(orig_to_site).strip()
            
            norm_key = normalize_key(item, to_site)
            item_part = norm_key[0]
            
            qty = row['Qty']
            time = row['Time']
            due_lt = row['Due_LT']
            
            # 디버깅: 처음 몇 개의 항목만 키 체크 출력
            # if idx < 5:
            #     print(f"확인 #{idx+1}: 키 정규화 ({item}, {orig_to_site}) -> {norm_key}")
            #     print(f"정확한 매칭: 이 키가 demand_sop_map에 있는지: {norm_key in demand_sop_map}")
                
            #     if norm_key not in demand_sop_map:
            #         # Item은 있지만 To_site가 다른 경우 찾기
            #         item_keys = [k for k in demand_sop_map.keys() if k[0] == item_part]
            #         if item_keys:
            #             print(f"  - Item '{item}'은 Demand에 있지만 To_site가 다릅니다. 가능한 To_site 값: {[k[1] for k in item_keys]}")
                        
            #             if use_flexible_matching:
            #                 print(f"  - 유연한 매칭 사용: Item만 일치하는 경우 허용 (possible_keys: {item_keys})")
            #         else:
            #             print(f"  - Item '{item}'은 Demand에 없습니다.")
            
            # 1. 정확한 매칭 시도 (Item + To_site)
            exact_match = norm_key in demand_sop_map
            
            # 2. 유연한 매칭 시도 (Item만 일치하고 To_site는 다름 또는 NaN)
            flexible_match = False
            flexible_match_key = None
            
            if not exact_match and use_flexible_matching:
                # To_site가 NaN인 경우 특별 처리
                if pd.isna(orig_to_site) or orig_to_site == '':
                    # 해당 Item에 대한 모든 가능한 키 찾기
                    item_keys = [k for k in demand_sop_map.keys() if k[0] == item_part]
                    
                    if item_keys:
                        # SOP가 가장 큰 To_site를 선택 (NaN인 경우에만)
                        flexible_match_key = max(item_keys, key=lambda k: demand_sop_map[k])
                        flexible_match = True
                        # if idx < 5:  # 디버깅용
                        #     print(f"  - To_site NaN 처리: Item={item}에 대해 Demand의 To_site '{flexible_match_key[1]}'로 대체")
                else:
                    # To_site가 있지만 정확한 매칭이 없는 경우
                    # 현재 To_site가 있는 그대로 사용 (해당 Item+To_site 조합이 Demand에 있는지 확인)
                    current_key = (item_part, to_site)
                    if current_key in demand_sop_map:
                        flexible_match_key = current_key
                        flexible_match = True
                        # if idx < 5:  # 디버깅용
                        #     print(f"  - 유연한 매칭: Result의 Item={item}, To_site={to_site}와 일치하는 Demand 키 발견")
                    else:
                        # 해당 Item에 대한 모든 가능한 To_site 찾기
                        item_keys = [k for k in demand_sop_map.keys() if k[0] == item_part]
                        
                        if item_keys:
                            # To_site가 있지만 Demand에 없는 경우, Demand에서 가장 가까운 To_site 찾기
                            # 여기서는 단순히 SOP가 가장 큰 것을 선택하지만, 더 복잡한 로직 적용 가능
                            flexible_match_key = max(item_keys, key=lambda k: demand_sop_map[k])
                            flexible_match = True
                            # if idx < 5:  # 디버깅용
                            #     print(f"  - 대체 To_site: Item={item}, To_site={to_site}는 Demand에 없어 '{flexible_match_key[1]}'로 대체")
            
            # 매칭 결과에 따라 in_demand 결정
            in_demand = exact_match or flexible_match
            
            # 매칭된 키에 따라 demand_sop 결정
            if exact_match:
                match_type = "exact"
                demand_sop = demand_sop_map[norm_key]
                match_key = norm_key
            elif flexible_match:
                match_type = "flexible"
                demand_sop = demand_sop_map[flexible_match_key]
                match_key = flexible_match_key
            else:
                match_type = "none"
                demand_sop = 0
                match_key = None
            
            # 조건 1: 시간 조건 - Time이 Due_LT 이하인지
            time_condition_met = time <= due_lt
            
            # 조건 2: 수량 조건 - Item과 To_site 조합의 총 생산량이 SOP 이상인지
            if exact_match:
                # 정확한 매칭인 경우 해당 Item+To_site에 대한 생산량만 확인
                qualified_qty = exact_match_qty.get(norm_key, 0)
                qty_condition_met = in_demand and qualified_qty >= demand_sop
            elif flexible_match:
                # 유연한 매칭의 경우, 동일 Item에 대한 To_site 별 처리 방식을 변경
                # 특정 To_site의 SOP를 그 To_site의 생산량만으로 채워야 하는 경우
                
                # 1. Result 파일에서 현재 Item과 동일한 To_site를 가진 모든 행 찾기
                same_item_to_site_rows = result_df[
                    (result_df['Item'].apply(lambda x: normalize_key(x, '')[0] == item_part)) &
                    (result_df['To_site'].apply(lambda x: normalize_key('', x)[1] == to_site))
                ]
                
                # 2. 해당 행들 중 Due_LT 내의 생산량 계산
                current_to_site_qty = sum(row['Qty'] for _, row in same_item_to_site_rows.iterrows() 
                                        if row['Time'] <= row['Due_LT'])
                
                # 3. 현재 To_site에 대한 SOP 가져오기
                current_to_site_sop = demand_sop_map.get(norm_key, 0)
                
                # 4. 현재 To_site에 대한 수량 조건 확인
                qty_condition_met = current_to_site_qty >= current_to_site_sop
                qualified_qty = current_to_site_qty
                
                # if idx < 5:  # 디버깅용
                #     print(f"  - 유연한 매칭 수량 확인: Item={item}, To_site={to_site}")
                #     print(f"    현재 To_site의 생산량: {current_to_site_qty}, SOP: {current_to_site_sop}")
                #     print(f"    수량 조건 충족 여부: {qty_condition_met}")
            else:
                qualified_qty = 0
                qty_condition_met = False
            
            # 두 조건 모두 만족해야 출하 가능
            is_shippable = in_demand and time_condition_met and qty_condition_met
            
            # 모델 단위 처리를 위한 레코드 저장
            record_key = match_key if match_key else norm_key
            if record_key not in model_records:
                model_records[record_key] = []
            model_records[record_key].append(idx)
            
            # 결과 저장
            result_analysis.append({
                'Index': idx,
                'Item': item,
                'To_site': to_site,
                'Original_To_site': orig_to_site,
                'NormalizedKey': norm_key,
                'MatchKey': match_key,
                'MatchType': match_type,
                'Line': row.get('Line', ''),
                'Time': time,
                'Due_LT': due_lt,
                'Qty': qty,
                'DemandSOP': demand_sop,
                'QualifiedQty': qualified_qty,  # Due_LT 내 총 생산량
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
        # print(f"출하 불가능 레코드 수: {len(unshippable_items)}")
        
        # 모델 기준 통계 계산
        model_stats = {}
        
        # 먼저 Demand에 있는 모든 모델에 대해 기본 통계 초기화
        for key, sop in demand_sop_map.items():
            model_stats[key] = {
                'total_records': 0,
                'success_records': 0,
                'sop': sop,
                'total_qty': 0,
                'success_qty': 0,
                'match_type': 'none'  # 기본값
            }
        
        # Result에서 각 레코드를 해당 모델의 통계에 반영
        for idx, row in analysis_df.iterrows():
            match_key = row['MatchKey']
            
            if match_key and match_key in model_stats:  # Demand에 있는 모델인 경우만 처리
                model_stats[match_key]['total_records'] += 1
                model_stats[match_key]['total_qty'] += row['Qty']
                model_stats[match_key]['match_type'] = row['MatchType']
                
                if row['IsShippable']:
                    model_stats[match_key]['success_records'] += 1
                    model_stats[match_key]['success_qty'] += row['Qty']
        
        # 당주 출하 만족률(수량 기준) 계산
        # 전체: Demand 시트의 동일한 Item+To_site의 SOP 합계
        total_sop = sum(demand_sop_map.values())
        
        # 성공: 출하 성공 판단된 아이템의 QTY
        success_qty = sum(stats['success_qty'] for stats in model_stats.values())
        
        qty_success_rate = success_qty / total_sop * 100 if total_sop > 0 else 0
        
        # 당주 출하 만족률(모델 기준) 계산
        # 전체 모델 수 (Demand 시트에 있는 Item+To_site 조합 수)
        total_models = len(demand_sop_map)  # Demand 시트에 있는 모델 수
        
        # 성공 모델 수 (Result에서 하나라도 출하 성공인 모델)
        # Demand에 있는 모델 중에서만 계산
        success_models = 0
        for key in demand_sop_map.keys():
            # Result에 해당 모델이 있고, 성공 레코드가 있는지 확인
            if key in model_stats and model_stats[key]['success_records'] > 0:
                success_models += 1
        
        model_success_rate = success_models / total_models * 100 if total_models > 0 else 0
        
        # 매칭 유형별 통계
        exact_match_count = sum(1 for row in result_analysis if row['MatchType'] == 'exact')
        flexible_match_count = sum(1 for row in result_analysis if row['MatchType'] == 'flexible')
        no_match_count = sum(1 for row in result_analysis if row['MatchType'] == 'none')
        
        # 통계 요약
        summary = {
            'total_sop': total_sop,
            'success_qty': success_qty,
            'qty_success_rate': qty_success_rate,
            'total_models': total_models,
            'success_models': success_models,
            'model_success_rate': model_success_rate,
            'exact_match_count': exact_match_count,
            'flexible_match_count': flexible_match_count,
            'no_match_count': no_match_count,
            'model_stats': model_stats  # 모델별 상세 통계
        }
        
        # 결과 출력
        print("\n===== 당주 출하 만족률 분석 결과 =====")
        print(f"Demand 시트에 있는 Item+To_site 조합 수: {total_models}")
        print(f"전체 SOP 수량: {total_sop:.0f}")
        print(f"출하 성공 수량(QTY): {success_qty:.0f}")
        print(f"당주 출하 만족률(수량 기준): {qty_success_rate:.2f}%")
        print(f"성공 모델 수: {success_models}")
        print(f"실패 모델 수: {total_models - success_models}")
        print(f"전체 모델 수: {total_models}")
        print(f"모델 기준 성공률: {model_success_rate:.2f}%")
        
        # 매칭 유형별 통계 출력
        print(f"\n===== 매칭 유형별 통계 =====")
        print(f"정확한 매칭 (Item+To_site): {exact_match_count}건")
        print(f"유연한 매칭 (Item만): {flexible_match_count}건")
        print(f"매칭 실패: {no_match_count}건")
        print(f"총 레코드 수: {len(result_analysis)}건")
        
        # 모델별 상세 정보 (샘플)
        # print("\n===== 모델별 상세 정보 (상위 5개) =====")
        # for i, (key, stats) in enumerate(list(model_stats.items())[:5]):
        #     item, to_site = key
        #     print(f"{i+1}. Item: {item}, To_site: {to_site}, 매칭 유형: {stats['match_type']}")
        #     print(f"   SOP: {stats['sop']}, 총 QTY: {stats['total_qty']}, 성공 QTY: {stats['success_qty']}")
        #     print(f"   레코드 수: {stats['total_records']}, 성공 레코드 수: {stats['success_records']}")
        
        # 출하 실패 항목 표시
        # print("\n===== 당주 출하 실패 항목 (상위 10개) =====")
        # Demand에 있는 실패 항목 중 Qty가 큰 순서로 정렬
        demand_failures = unshippable_items[unshippable_items['InDemand']]
        if len(demand_failures) > 0:
            # top_failures = demand_failures.sort_values(by='Qty', ascending=False).head(10)
            # print(top_failures[['Item', 'To_site', 'MatchType', 'Line', 'Time', 'Due_LT', 'Qty', 'DemandSOP', 'TimeConditionMet', 'QtyConditionMet']])
            
            # 실패 이유 분석
            time_condition_fail = len(demand_failures[~demand_failures['TimeConditionMet']])
            qty_condition_fail = len(demand_failures[~demand_failures['QtyConditionMet']])
            both_condition_fail = len(demand_failures[~demand_failures['TimeConditionMet'] & ~demand_failures['QtyConditionMet']])
            
            print(f"\n실패 원인 분석 (Demand에 있는 항목만):")
            print(f"- Time > Due_LT 조건 위반: {time_condition_fail}건")
            print(f"- 생산량 < SOP 조건 위반: {qty_condition_fail}건") 
            print(f"- 두 조건 모두 위반: {both_condition_fail}건")
        else:
            print("Demand에 있는 항목 중 출하 실패 항목이 없습니다.")
        
        return result_df, summary, analysis_df
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()  # 상세 오류 정보 출력
        return None, None, None
        