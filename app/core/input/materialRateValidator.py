import pandas as pd
import numpy as np
import re
from app.models.input.material import process_material_satisfaction_data

# 자재 만족률 분석
def calculate_material_satisfaction(data, threshold=90) :
    if isinstance(data, dict) and 'error' in data :
        return data
    
    required_keys = ['material_df', 'material_item_df', 'demand_df']

    for key in required_keys :
        if key not in data :
            return {'error' : f'필수 데이터 누락 : {key}'}
        
    try :
        material_df = data['material_df']
        material_item_df = data['material_item_df']
        demand_df = data['demand_df']
        material_equal_df = data.get('material_equal_df')
        date_columns = data.get('date_columns', [])

        if isinstance(material_df, pd.DataFrame) and date_columns :
            material_df['Original_On_Hand'] = material_df['On-Hand'].copy()

            for idx, row in material_df.iterrows() :
                future_supply = 0

                for date_col in date_columns :
                    if date_col in material_df.columns and pd.notnull(row[date_col]) and isinstance(row[date_col], (int, float)) :
                        future_supply += row[date_col]

                material_df.at[idx, 'On-Hand'] = row['Original_On_Hand'] + future_supply

            data['date_columns_used'] = date_columns

            if date_columns :
                data['start_date'] = date_columns[0]
                data['end_date'] = date_columns[-1]
            
        substitute_groups, material_to_group = create_substitute_groups(material_equal_df)

        item_to_materials = map_items_to_materials(material_item_df, demand_df)
        material_onhand = extract_material_onhand(material_df)
        material_requirements = calculate_material_requirements(item_to_materials, demand_df)

        group_requirements, group_onhand = calculate_group_values(
            substitute_groups, material_requirements, material_onhand
        )

        item_producible = calculate_item_producible_quantity(
            item_to_materials, material_onhand, material_to_group,
            group_onhand, material_requirements, group_requirements, demand_df
        )

        item_satisfaction_rates = calculate_item_satisfaction_rates(item_producible, demand_df)
        passed_items = [item for item, rate in item_satisfaction_rates.items() if rate >= threshold]
        failed_items = [item for item, rate in item_satisfaction_rates.items() if rate < threshold]

        rows = []

        for item, rate in item_satisfaction_rates.items() :
            producible = item_producible.get(item, 0)
            pass_status = '통과' if rate >= threshold else '미통과'

            demand = 0

            if 'Item' in demand_df.columns :
                item_rows = demand_df[demand_df['Item'] == item]

                if not item_rows.empty :
                    demand = item_rows['MFG'].values[0]

            rows.append({
                '모델명' : item,
                '수요량' : demand,
                '생산가능수량' : producible,
                '자재만족률' : round(rate, 2),
                '통과여부' : pass_status
            })

        result_df = pd.DataFrame(rows)

        total_demand = result_df['수요량'].sum()
        total_producible = result_df['생산가능수량'].sum()
        overall_rate = (total_producible / total_demand * 100) if total_demand > 0 else 100

        date_range_info = "없음"
        if 'start_date' in data and 'end_date' in data :
            date_range_info = f'{data['start_date']} ~ {data['end_date']}'

        summary = {
            "통과 모델 수": len(passed_items),
            "전체 모델 수": len(item_satisfaction_rates),
            "통과율(%)": round(len(passed_items) / len(item_satisfaction_rates) * 100 if item_satisfaction_rates else 0, 2),
            "통과 기준(%)": threshold,
            "입고 날짜 범위": date_range_info,
            "전체 수요량": total_demand,
            "전체 생산가능수량": total_producible,
            "전체 자재만족률(%)": round(overall_rate, 2)
        }

        result = {
            "results_table": result_df,
            "summary": summary,
            "item_satisfaction_rates": item_satisfaction_rates,
            "item_producible": item_producible,
            "passed_items": passed_items,
            "failed_items": failed_items,
            "threshold": threshold,
            "material_requirements": material_requirements,
            "material_onhand": material_onhand
        }

        if 'Original_On_Hand' in material_df.columns :
            material_df['On-Hand'] = material_df['Original_On_Hand']
            material_df.drop(columns=['Original_On_Hand'], inplace=True)

        return result
    
    except Exception as e :
        return {'error' : f'자재만족률 분석 중 오류 발생 : {str(e)}'}
    
# 날짜 컬럼 정렬 함수
def sort_date_columns(date_columns) :
    def extract_date(col) :
        date_str = str(col).split('(')[0]

        try :
            month, day = map(int, date_str.split('/'))

            return month * 100 + day
        except (ValueError, IndexError) :
            return float('inf')
        
    return sorted(date_columns, key = extract_date)


# 대체 가능한 자재 그룹 생성
def create_substitute_groups(material_equal_df) :
    substitute_groups = []
    material_to_group = {}

    if material_equal_df is None or isinstance(material_equal_df, pd.DataFrame) and material_equal_df.empty :
        return substitute_groups, material_to_group
    
    valid_columns = [col for col in material_equal_df.columns if col.startswith('Material')]

    if not valid_columns :
        return substitute_groups, material_to_group
    
    for idx, row in material_equal_df.iterrows() :
        group = []

        for col in valid_columns :
            if pd.notnull(row[col]) and row[col] :
                group.append(row[col])

        if group :
            group_idx = len(substitute_groups)
            substitute_groups.append(group)

            for material in group :
                material_to_group[material] = group_idx

    return substitute_groups, material_to_group

# 수요 아이템별로 필요한 자재 매핑
def map_items_to_materials(material_item_df, demand_df) :
    item_to_materials = {}

    if material_item_df is None or material_item_df.empty or demand_df is None or demand_df.empty :
        return item_to_materials
    
    model_columns = [col for col in material_item_df.columns if col.startswith('Top_Model_')]

    if not model_columns :
        return item_to_materials
    
    active_materials = material_item_df[material_item_df['Active_OX'] == 'O'].copy()

    for idx, row in demand_df.iterrows() :
        item = row['Item'] if 'Item' in row else row.name
        item_to_materials[item] = []

        for mat_idx, mat_row in active_materials.iterrows() :
            material = mat_row['Material']

            for col in model_columns :
                if pd.notnull(mat_row[col]) and mat_row[col] :
                    if match_pattern(item, mat_row[col]) :
                        item_to_materials[item].append(material)
                        break

    return item_to_materials

# 와일드카드 패턴 확인
def match_pattern(item, pattern) :
    parts = pattern.split('*')

    if not item.startswith(parts[0]) :
        return False
    
    if not item.endswith(parts[-1]) :
        return False
    
    current_pos = len(parts[0])

    for part in parts[1:-1] :
        if part :
            pos = item.find(part, current_pos)

            if pos == -1 :
                return False
            
            current_pos = pos + len(part)

    return True

# 자재별 On-Hand 추출
def extract_material_onhand(material_df) :
    material_onhand = {}

    if material_df is None or material_df.empty :
        return material_onhand
    
    active_materials = material_df[material_df['Active_OX'] == 'O'].copy()

    for idx, row in active_materials.iterrows() :
        material = row['Material']
        onhand = row['On-Hand']
        material_onhand[material] = onhand

    return material_onhand

# 자재별 총 소요량 계산
def calculate_material_requirements(item_to_materials, demand_df) :
    material_requirements = {}

    if not item_to_materials or demand_df is None or demand_df.empty :
        return material_requirements
    
    for item, materials in item_to_materials.items() :
        demand = 0

        if 'Item' in demand_df.columns :
            item_rows = demand_df[demand_df['Item'] == item]

            if not item_rows.empty :
                demand = item_rows['MFG'].values[0]

        else :
            if item in demand_df.index :
                demand = demand_df.loc[item, 'MFG']

        if demand > 0 :
            for material in materials :
                if material in material_requirements :
                    material_requirements[material] += demand
                else :
                    material_requirements[material] = demand

    return material_requirements

# 그룹별 총 소요량과 On-Hand 계산
def calculate_group_values(substitute_groups, material_requirements, material_onhand) :
    group_requirements = {}
    group_onhand = {}

    for group_idx, group in enumerate(substitute_groups) :
        group_requirements[group_idx] = sum(material_requirements.get(material, 0) for material in group)
        group_onhand[group_idx] = sum(material_onhand.get(material, 0) for material in group)

    return group_requirements, group_onhand

# 모델별 생산 가능 수량 계산
def calculate_item_producible_quantity(item_to_materials, material_onhand, material_to_group,
                                       group_onhand, material_requirements, group_requirements, demand_df) :
    item_producible = {}

    for item, materials in item_to_materials.items() :
        demand = 0

        if 'Item' in demand_df.columns :
            item_rows = demand_df[demand_df['Item'] == item]

            if not item_rows.empty :
                demand = item_rows['MFG'].values[0]

        else :
            if item in demand_df.index :
                demand = demand_df.loc[item, 'MFG']

        if demand > 0 :
            material_producible = []

            for material in materials :
                if material in material_to_group :
                    group_idx = material_to_group[material]

                    if group_requirements[group_idx] > 0 :
                        item_req = demand
                        ratio = item_req / group_requirements[group_idx]

                        allocated_onhand = group_onhand[group_idx] * ratio
                        producible = int(allocated_onhand)
                    else :
                        producible = demand
                else :
                    if material in material_onhand :
                        material_oh = material_onhand[material]

                        if material in material_requirements and material_requirements[material] > 0 :
                            ratio = demand / material_requirements[material]
                            allocated_onhand = material_oh * ratio
                            producible = int(allocated_onhand)
                        else :
                            producible = demand if material_oh >= demand else int(material_oh)
                    else :
                        producible = 0

                material_producible.append(producible)

            if material_producible :
                item_producible[item] = min(material_producible)
            else :
                item_producible[item] = demand
        else :
            item_producible[item] = 0

    return item_producible

# 모델별 자재만족률 계산
def calculate_item_satisfaction_rates(item_producible, demand_df) :
    item_satisfaction_rates = {}

    for item, producible in item_producible.items() :
        demand = 0

        if 'Item' in demand_df.columns :
            item_rows = demand_df[demand_df['Item'] == item]

            if not item_rows.empty :
                demand = item_rows['MFG'].values[0]

        else :
            if item in demand_df.index :
                demand = demand_df.loc[item, 'MFG']

        if demand > 0 :
            item_satisfaction_rates[item] = (producible / demand) * 100
        else :
            item_satisfaction_rates[item] = 100.0

    return item_satisfaction_rates

# 자재만족률 계산 통합
def analyze_material_satisfaction_all(threshold=90) :
    try :
        data = process_material_satisfaction_data()

        if isinstance(data, dict) and 'error' in data :
            return data
        
        results = calculate_material_satisfaction(data, threshold)

        print_material_satisfaction_summary(results)

        return results
    except Exception as e :
        print(f'자재만족률 분석 중 오류 발생 : {str(e)}')
        return {'error' : f'자재만족률 분석 중 오류 발생 : {str(e)}'}

# 자재만족률 분석 결과의 요약 정보 생성
def get_material_satisfaction_summary(results, threshold=None) :
    if isinstance(results, dict) and 'error' in results :
        return f'오류 발생 : {results['error']}'
    
    if 'summary' not in results or 'results_table' not in results :
        return '분석 결과가 올바르지 않습니다'
    
    summary = results['summary']
    results_table = results['results_table']

    if threshold is None :
        threshold = summary['통과 기준(%)']

    failed_models = results_table[results_table['자재만족률'] < threshold].sort_values(by='자재만족률', ascending=True)

    summary_text = []
    summary_text.append(f"[자재만족률 분석 결과 요약]")
    summary_text.append("=" * 70)
    summary_text.append(f"통과 기준: {summary['통과 기준(%)']}%")
    summary_text.append(f"전체 모델 수: {summary['전체 모델 수']}")
    summary_text.append(f"통과 모델 수: {summary['통과 모델 수']}")
    summary_text.append(f"통과율: {summary['통과율(%)']}%")
    summary_text.append("")

    if failed_models.empty :
        summary_text.append(f'자재만족률이 {threshold}% 미만인 모델이 없습니다')

    else :
        failed_count = len(failed_models)
        summary_text.append(f"[자재만족률이 {threshold}% 미만인 모델 목록 (총 {failed_count}개)]")
        summary_text.append("-" * 70)
        summary_text.append(f"{'모델명':<30} {'수요량':<10} {'생산가능수량':<15} {'자재만족률(%)':<15} {'통과여부':<10}")
        summary_text.append("-" * 70)

        for _, row in failed_models.iterrows() :
            model = row['모델명']
            demand = row['수요량']
            producible = row['생산가능수량']
            rate = row['자재만족률(%)']
            status = row['통과여부']

            summary_text.append(f'{model:<30} {demand:<10.0f} {producible:<15.0f} {rate:<15.2f} {status:<10}')

        return '\n'.join(summary_text)
    
# 자재만족률 분석 결과 로그 출력
def print_material_satisfaction_summary(results) :
    if isinstance(results, dict) and 'error' in results :
        print(f'오류 발생 : {results['error']}')
        return
    
    if 'summary' not in results or 'results_table' not in results :
        print('분석 결과가 올바르지 않습니다')
        return
    
    summary = results['summary']
    results_table = results['results_table']
    threshold = summary['통과 기준(%)']

    print("\n[자재만족률 분석 결과 요약]")
    print("=" * 70)
    print(f"통과 기준: {summary['통과 기준(%)']}%")
    print(f"전체 모델 수: {summary['전체 모델 수']}")
    print(f"통과 모델 수: {summary['통과 모델 수']} ({summary['통과율(%)']}%)")
    print(f"미통과 모델 수: {summary['전체 모델 수'] - summary['통과 모델 수']} ({100 - summary['통과율(%)']}%)")
    
    if '입고 날짜 범위' in summary :
        print(f'입고 날짜 범위 : {summary['입고 날짜 범위']}')

    failed_models = results_table[results_table['통과여부'] == '미통과'].sort_values(by='자재만족률', ascending=True)

    if failed_models.empty :
        print(f'\n자재만족률이 {threshold}% 미만인 모델이 없습니다')
    else :
        failed_count = len(failed_models)

        print(f"\n[자재만족률이 {threshold}% 미만인 모델 목록 (총 {failed_count}개)]")
        print("-" * 70)
        print(f"{'모델명':<30} {'수요량':<10} {'생산가능수량':<15} {'자재만족률':<15} {'통과여부':<10}")
        print("-" * 70)

        for _, row in failed_models.iterrows() :
            model = row['모델명']
            demand = row['수요량']
            producible = row['생산가능수량']
            rate = row['자재만족률']
            status = row['통과여부']

            print(f"{model:<30} {demand:<10.0f} {producible:<15.0f} {rate:<15.2f} {status:<10}")

    passed_models = results_table[results_table['통과여부'] == '통과']