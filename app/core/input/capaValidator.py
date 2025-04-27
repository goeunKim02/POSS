import pandas as pd
import numpy as np
from scipy.optimize import linprog

# 제조동별 물량 분배 비율이 제약 조건을 통과하는지 확인하는 함수 (선형 계획법)
def validate_distribution_ratios(processed_data):
    demand_items = processed_data['demand_items']
    project_to_buildings = processed_data['project_to_buildings']
    building_constraints = processed_data['building_constraints']

    # 현재 분배 상태 분석
    current_distribution = analyze_current_distribution(demand_items, project_to_buildings)
    total_quantity = sum(current_distribution.values())

    if total_quantity > 0:
        building_ratios = {
            building: quantity / total_quantity
            for building, quantity in current_distribution.items()
        }
    else:
        building_ratios = {building: 0 for building in current_distribution}

    # 현재 분배가 제약 조건을 위반하는지 확인
    violations = {}
    distribution_valid = True

    for building, ratio in building_ratios.items():
        if building in building_constraints:
            lower_limit = building_constraints[building]['lower_limit']
            upper_limit = building_constraints[building]['upper_limit']

            if ratio < lower_limit:
                violations[building] = {
                    'type': 'below_limit',
                    'current_ratio': ratio,
                    'limit': lower_limit,
                    'gap': lower_limit - ratio
                }
                distribution_valid = False
            
            elif ratio > upper_limit:
                violations[building] = {
                    'type': 'above_limit',
                    'current_ratio': ratio,
                    'limit': upper_limit,
                    'gap': ratio - upper_limit
                }
                distribution_valid = False

    alternative_valid = False

    if not distribution_valid:
        # 선형 계획법을 사용하여 최적의 분배 찾기
        fixed_projects, flexible_projects = classify_projects(demand_items, project_to_buildings)
        
        # 선형 계획법으로 해결책을 찾으면 그것을 현재 분배로 설정
        optimal_result = find_optimal_distribution_with_lp(
            fixed_projects, flexible_projects, project_to_buildings, building_constraints)
        
        if optimal_result['success']:
            # 최적해를 찾았으면 그것을 현재 분배로 업데이트
            current_distribution = optimal_result['distribution']
            total_quantity = sum(current_distribution.values())
            
            building_ratios = {
                building: quantity / total_quantity
                for building, quantity in current_distribution.items()
            }
            
            # 위반 사항 초기화
            violations = {}
            distribution_valid = True
            alternative_valid = True
        else:
            alternative_valid = False

    return {
        'current_distribution': current_distribution,
        'building_ratios': building_ratios,
        'violations': violations,
        'current_valid': distribution_valid,
        'alternative_possible': alternative_valid,
        'has_anomalies': not (distribution_valid or alternative_valid)
    }

# 선형 계획법을 사용한 최적 분배 함수
def find_optimal_distribution_with_lp(fixed_projects, flexible_projects, project_to_buildings, building_constraints):
    # 모든 제조동 리스트
    buildings = list(building_constraints.keys())
    n_buildings = len(buildings)
    
    # 변수 준비
    fixed_allocation = {building: 0 for building in buildings}
    
    # 고정 프로젝트 물량 계산
    for item in fixed_projects:
        project = item.get('Basic2', item.get('Project', ''))
        mfg_quantity = item.get('MFG', 0)
        buildings_for_project = project_to_buildings.get(project, [])
        
        if buildings_for_project and buildings_for_project[0] in fixed_allocation:
            fixed_allocation[buildings_for_project[0]] += mfg_quantity
    
    # 유연한 프로젝트별 변수 설정
    variables = []
    variable_map = {}
    
    idx = 0
    project_quantities = {}  # 프로젝트별 총 물량 추적
    
    for item in flexible_projects:
        project = item.get('Basic2', item.get('Project', ''))
        mfg_quantity = item.get('MFG', 0)
        buildings_for_project = project_to_buildings.get(project, [])
        
        if not buildings_for_project:
            continue
            
        # 프로젝트별 총 물량 누적
        project_quantities[project] = project_quantities.get(project, 0) + mfg_quantity
    
    # 프로젝트별로 변수 생성
    for project, total_quantity in project_quantities.items():
        buildings_for_project = []
        
        # 해당 프로젝트가 갈 수 있는 모든 제조동 찾기
        for item in flexible_projects:
            item_project = item.get('Basic2', item.get('Project', ''))
            if item_project == project:
                buildings_for_item = project_to_buildings.get(item_project, [])
                for b in buildings_for_item:
                    if b not in buildings_for_project:
                        buildings_for_project.append(b)
        
        for building in buildings_for_project:
            if building in buildings:
                variables.append({
                    'project': project,
                    'building': building,
                    'quantity': total_quantity,
                    'index': idx
                })
                variable_map[(project, building)] = idx
                idx += 1
    
    if not variables:
        return {'success': False, 'distribution': None}
    
    n_vars = len(variables)
    
    # 목적 함수
    c = np.zeros(n_vars)
    
    # 제약 조건 설정
    A_eq = []
    b_eq = []
    A_ub = []
    b_ub = []
    
    projects_in_variables = set(v['project'] for v in variables)
    for project in projects_in_variables:
        row = np.zeros(n_vars)
        for v in variables:
            if v['project'] == project:
                row[v['index']] = 1
        A_eq.append(row)
        b_eq.append(1.0)
    
    # 각 제조동의 비율 제약 확인
    total_fixed = sum(fixed_allocation.values())
    total_flexible = sum(project_quantities.values())
    total_quantity = total_fixed + total_flexible
    
    if total_quantity == 0:
        return {'success': False, 'distribution': None}
    
    # 하한선 제약
    for _, building in enumerate(buildings):
        if building in building_constraints:
            lower_limit = building_constraints[building]['lower_limit']
            required_quantity = lower_limit * total_quantity
            
            row = np.zeros(n_vars)
            for v in variables:
                if v['building'] == building:
                    row[v['index']] = -v['quantity']
            
            A_ub.append(row)
            b_ub.append(-(required_quantity - fixed_allocation[building]))
    
    # 상한선 제약
    for _, building in enumerate(buildings):
        if building in building_constraints:
            upper_limit = building_constraints[building]['upper_limit']
            max_quantity = upper_limit * total_quantity
            
            row = np.zeros(n_vars)
            for v in variables:
                if v['building'] == building:
                    row[v['index']] = v['quantity']
            
            A_ub.append(row)
            b_ub.append(max_quantity - fixed_allocation[building])
    
    # 변수 범위 제약 (0 <= x <= 1)
    bounds = [(0, 1) for _ in range(n_vars)]
    
    try:
        # 선형 계획법 실행
        result = linprog(c, A_eq=A_eq if A_eq else None, b_eq=b_eq if b_eq else None,
                        A_ub=A_ub if A_ub else None, b_ub=b_ub if b_ub else None,
                        bounds=bounds, method='highs')
        
        if result.success:
            # 결과 분배 계산
            final_allocation = {building: fixed_allocation[building] for building in buildings}
            
            for v in variables:
                allocation_ratio = result.x[v['index']]
                building = v['building']
                quantity = v['quantity']
                final_allocation[building] += allocation_ratio * quantity
            
            # 최종 비율 확인
            total = sum(final_allocation.values())
            for building in buildings:
                if building in building_constraints:
                    ratio = final_allocation[building] / total
                    lower = building_constraints[building]['lower_limit']
                    upper = building_constraints[building]['upper_limit']
                    
                    if ratio < lower - 1e-6 or ratio > upper + 1e-6:
                        return {'success': False, 'distribution': None}
            
            return {'success': True, 'distribution': final_allocation}
        
    except Exception as e:
        print(f"선형 계획법 오류: {e}")
    
    return {'success': False, 'distribution': None}

# 현재 분배 상태 분석 함수
def analyze_current_distribution(demand_items, project_to_buildings):
    all_buildings = set()
    
    for buildings in project_to_buildings.values():
        all_buildings.update(buildings)
    
    building_quantity = {building: 0 for building in all_buildings}
    
    for item in demand_items:
        project = item.get('Basic2', item.get('Project', ''))
        mfg_quantity = item.get('MFG', 0)
        buildings = project_to_buildings.get(project, [])
        
        if not buildings:
            continue
        
        if len(buildings) == 1:
            building_quantity[buildings[0]] += mfg_quantity
        else:
            quantity_per_building = mfg_quantity / len(buildings)
            
            for building in buildings:
                building_quantity[building] += quantity_per_building
    
    return building_quantity

# 프로젝트 분류 함수
def classify_projects(demand_items, project_to_buildings):
    fixed_projects = []
    flexible_projects = []
    
    for item in demand_items:
        project = item.get('Basic2', item.get('Project', ''))
        buildings = project_to_buildings.get(project, [])
        
        if len(buildings) <= 1:
            fixed_projects.append(item)
        else:
            flexible_projects.append(item)
    
    return fixed_projects, flexible_projects