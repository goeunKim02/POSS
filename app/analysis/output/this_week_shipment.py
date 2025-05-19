import pandas as pd
import numpy as np
import os
from app.models.common.file_store import FilePaths, DataStore

"""
결과 데이터를 분석하여 출하 성능 결과를 반환
"""
def analyze_and_get_results(result_data=None):
    return analyze_shipment_performance(result_data)

"""
Result 파일을 사용하여 당주 출하 실패 건과 만족률을 계산
출하 가능 조건: Item+Tosite 조합별로 Due_LT 내 생산량이 SOP 이상
"""
def analyze_shipment_performance(result_data=None):
    try:
        # 1. 결과 데이터 로드
        if result_data is not None:
            # 직접 전달된 데이터 사용
            result_df = result_data.copy()
        else:
            # DataStore에서 확인
            result_df = DataStore.get("result_data")
            if result_df is None:
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
                        return None, None, None
                        
        # 결과 데이터가 없으면 종료
        if result_df is None:
            return None, None, None
        
        # Tosite 컬럼 확인 - 없으면 To_site 사용
        if 'Tosite' not in result_df.columns:
            if 'To_site' in result_df.columns:
                result_df['Tosite'] = result_df['To_site']
            else:
                result_df['Tosite'] = ""
                
        # 호환성을 위해 Tosite_group과 To_site 컬럼도 유지
        if 'Tosite_group' not in result_df.columns:
            result_df['Tosite_group'] = result_df['Tosite']
        if 'To_site' not in result_df.columns:
            result_df['To_site'] = result_df['Tosite']
        
        # 데이터 타입 변환
        result_df['Due_LT'] = pd.to_numeric(result_df['Due_LT'], errors='coerce').fillna(0).astype(int)
        result_df['Time'] = pd.to_numeric(result_df['Time'], errors='coerce').fillna(0).astype(int)
        result_df['Qty'] = pd.to_numeric(result_df['Qty'], errors='coerce').fillna(0).astype(int)
        
        # Tosite 컬럼 확인 - 없으면 Tosite_group 사용
        if 'To_site' not in result_df.columns:
            if 'Tosite_group' in result_df.columns:
                result_df['Tosite'] = result_df['Tosite_group']
            else:
                # To_site 컬럼이 있는지 확인
                if 'ToSite' in result_df.columns:
                    result_df['Tosite'] = result_df['To_site']
                else:
                    result_df['Tosite'] = ""
                    
        # 호환성을 위해 Tosite_group과 To_site 컬럼도 유지
        if 'Tosite_group' not in result_df.columns:
            result_df['Tosite_group'] = result_df['Tosite']
        if 'To_site' not in result_df.columns:
            result_df['To_site'] = result_df['Tosite']
            
        # SOP 컬럼 확인 - 결과 파일 내에 SOP 컬럼이 있다고 가정
        if 'SOP' not in result_df.columns:
            # Item+Tosite 별로 그룹화하여 Qty 합계 계산 -> 이를 SOP로 가정
            grouped = result_df.groupby(['Item', 'Tosite'])['Qty'].sum().reset_index()
            grouped.rename(columns={'Qty': 'SOP'}, inplace=True)
            
            # 원본 데이터프레임에 SOP 정보 병합
            result_df = pd.merge(
                result_df, 
                grouped[['Item', 'Tosite', 'SOP']], 
                on=['Item', 'Tosite'], 
                how='left'
            )
        else:
            # SOP 컬럼이 있는 경우 숫자로 변환
            result_df['SOP'] = pd.to_numeric(result_df['SOP'], errors='coerce').fillna(0).astype(int)
        
        # 결과 분석을 위한 데이터 준비
        models = []
        analysis_records = []
        
        # 1. Item+Tosite 조합으로 모델 데이터 그룹화
        model_groups = result_df.groupby(['Item', 'Tosite'])
        
        # 2. 각 모델별로 데이터 분석
        for (item, tosite), group in model_groups:
            # 해당 모델의 SOP 값 (모든 row에서 동일하므로 첫 번째 값 사용)
            sop = group['SOP'].iloc[0]
            
            # Due_LT 내 생산량 계산 (각 행의 Time이 Due_LT 이하인 경우만 합산)
            due_lt_production = group[group['Time'] <= group['Due_LT']]['Qty'].sum()
            
            # 전체 생산량 (Time과 상관없이 모든 생산량)
            total_production = group['Qty'].sum()
            
            # 출하 성공 여부 계산 (Due_LT 내 생산량 >= SOP)
            is_shippable = due_lt_production >= sop
            
            # 모델 정보 저장
            model_info = {
                'Item': item,
                'Tosite': tosite,
                'Tosite_group': tosite,  # 호환성 유지
                'To_site': tosite,       # 호환성 유지
                'SOP': sop,
                'DueLTProduction': due_lt_production,
                'TotalProduction': total_production,
                'IsShippable': is_shippable,
                'ShipmentStatus': "출하가능" if is_shippable else "출하실패",
                'FailureReason': "" if is_shippable else "Qty<SOP" if due_lt_production < sop else "Unknown"
            }
            models.append(model_info)
            
            # 해당 모델의 각 행에 대한 상세 분석 정보 저장
            for idx, row in group.iterrows():
                time_condition_met = row['Time'] <= row['Due_LT']
                
                record = {
                    'Index': idx,
                    'Item': item,
                    'Tosite': tosite,
                    'Tosite_group': tosite,  # 호환성 유지
                    'To_site': tosite,       # 호환성 유지
                    'Line': row.get('Line', ''),
                    'Time': row['Time'],
                    'Due_LT': row['Due_LT'],
                    'Qty': row['Qty'],
                    'SOP': sop,
                    'DueLTProduction': due_lt_production,
                    'TotalProduction': total_production,
                    'TimeConditionMet': time_condition_met,
                    'QtyConditionMet': due_lt_production >= sop,
                    'IsShippable': is_shippable,
                    'MatchType': "exact",  # 유연한 매칭은 현재 사용하지 않음
                    'FailureReason': "" if is_shippable else "Qty<SOP" if due_lt_production < sop else "Unknown"
                }
                analysis_records.append(record)

        # 분석 결과를 데이터프레임으로 변환
        models_df = pd.DataFrame(models)
        analysis_df = pd.DataFrame(analysis_records)

        # ShipmentStatus 컬럼 추가
        analysis_df['ShipmentStatus'] = analysis_df['IsShippable'].apply(
            lambda x: "출하가능" if x else "출하실패"
        )
        
        # 원본 데이터프레임에 출하 상태 및 실패 이유 추가
        result_df = pd.merge(
            result_df,
            analysis_df[['Index', 'IsShippable', 'FailureReason']],
            left_index=True,
            right_on='Index',
            how='left'
        )
        
        # 통계 요약 계산
        total_models = len(models)
        success_models = sum(1 for model in models if model['IsShippable'])
        model_success_rate = (success_models / total_models * 100) if total_models > 0 else 0
        
        total_production = sum(model['TotalProduction'] for model in models)
        success_production = sum(model['TotalProduction'] for model in models if model['IsShippable'])
        qty_success_rate = (success_production / total_production * 100) if total_production > 0 else 0
        
        # 총 SOP 합계
        total_sop = sum(model['SOP'] for model in models)
        
        # 통계 요약 생성
        summary = {
            'total_models': total_models,
            'success_models': success_models,
            'model_success_rate': model_success_rate,
            'total_produced_qty': total_production,
            'success_qty': success_production,
            'qty_success_rate': qty_success_rate,
            'total_sop': total_sop,
            'models_df': models_df,  # 모델 DataFrame 추가
            'model_stats': {i: model for i, model in enumerate(models)}  # 모델별 상세 통계
        }
        
        return result_df, summary, analysis_df
        
    except Exception as e:
        import traceback
        traceback.print_exc()  # 상세 오류 정보 출력
        return None, None, None