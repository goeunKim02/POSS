import random

# 제조동별 물량 분배 비율이 제약 조건을 통과하는지 확인하는 함수
def validate_distribution_ratios(processed_data) :
    demand_items = processed_data['demand_items']
    project_to_buildings = processed_data['project_to_buildings']
    building_constraints = processed_data['building_constraints']

    current_distribution = analyze_current_distribution(demand_items, project_to_buildings)
    total_quantity = sum(current_distribution.values())

    if total_quantity > 0 :
        building_ratios = {
            building : quantity / total_quantity
            for building, quantity in current_distribution.items()
        }
    else :
        building_ratios = {building: 0 for building in current_distribution}

    violations = {}
    distribution_valid = True

    for building, ratio in building_ratios.items() :
        if building in building_constraints :
            lower_limit = building_constraints[building]['lower_limit']
            upper_limit = building_constraints[building]['upper_limit']

            if ratio < lower_limit :
                violations[building] = {
                    'type' : 'below_limit',
                    'current_ratio' : ratio,
                    'limit' : lower_limit,
                    'gap' : lower_limit - ratio
                }
                distribution_valid = False
            
            elif ratio > upper_limit :
                violations[building] = {
                    'type' : 'above_limit',
                    'current_ratio' : ratio,
                    'limit' : upper_limit,
                    'gap' : ratio - upper_limit
                }
                distribution_valid = False

    alternative_valid = False

    if not distribution_valid :
        fixed_projects, flexible_projects = classify_projects(demand_items, project_to_buildings)

        alternative_valid = find_valid_distribution(fixed_projects, flexible_projects, project_to_buildings, building_constraints)

    return {
        'current_distribution' : current_distribution,
        'building_ratios' : building_ratios,
        'violations' : violations,
        'current_valid' : distribution_valid,
        'alternative_possible' : alternative_valid,
        'has_anomalies' : not (distribution_valid or alternative_valid)
    }

# 휴리스틱 알고리즘을 위한 현재 분배 상태 분석 함수
def analyze_current_distribution(demand_items, project_to_buildings) :
    all_buildings = set()

    for buildings in project_to_buildings.values() :
        all_buildings.update(buildings)

    building_quantity = {building: 0 for building in all_buildings}

    for item in demand_items :
        project = item.get('Basic2', item.get('Project', ''))
        mfg_quantity = item.get('MFG', 0)
        buildings = project_to_buildings.get(project, [])

        if not buildings :
            continue

        if len(buildings) == 1 :
            building_quantity[buildings[0]] += mfg_quantity
        else :
            quantity_per_building = mfg_quantity / len(buildings)

            for building in buildings :
                building_quantity[building] += quantity_per_building

    return building_quantity

# 프로젝트 분류 함수 (고정(단일) 프로젝트랑 유연 프로젝트로 분류)
# 고정 프로젝트란, 특정 동에서만 제작 가능한 프로젝트
def classify_projects(demand_items, project_to_buildings) :
    fixed_projects = []
    flexible_projects = []

    for item in demand_items :
        project = item.get('Basic2', item.get('Project', ''))
        buildings = project_to_buildings.get(project, [])

        if len(buildings) <= 1 :
            fixed_projects.append(item)
        else :
            flexible_projects.append(item)

    return fixed_projects, flexible_projects

# 유효 분배 탐색 함수
def find_valid_distribution(fixed_projects, flexible_projects, project_to_buildings, building_constraints) :
    all_buildings = set(building_constraints.keys())
    building_quantity = {building : 0 for building in all_buildings}

    for item in fixed_projects :
        project = item.get('Basic2', item.get('Project', ''))
        mfg_quantity = item.get('MFG', 0)
        buildings = project_to_buildings.get(project, [])

        if buildings and buildings[0] in building_quantity :
            building_quantity[buildings[0]] += mfg_quantity
    
    # 물량 분할 할당 시도
    if try_distribution_with_splitting(building_quantity.copy(), flexible_projects,
                                      project_to_buildings, building_constraints):
        return True

    # 물량 기준 정렬 시도 (큰 물량부터)
    if try_distribution_strategy(building_quantity.copy(), flexible_projects,
                                 project_to_buildings, building_constraints,
                                 sort_key=lambda x: x.get('MFG', 0), reverse=True) :
        return True
    
    # 물량 기준 정렬 시도 (작은 물량부터)
    if try_distribution_strategy(building_quantity.copy(), flexible_projects,
                                 project_to_buildings, building_constraints,
                                 sort_key=lambda x: x.get('MFG', 0), reverse=False) :
        return True
    
    # 제조동 선택지 기준 정렬 시도
    if try_distribution_strategy(building_quantity.copy(), flexible_projects,
                                 project_to_buildings, building_constraints,
                                 sort_key=lambda x : len(project_to_buildings.get(x.get('Basic2', x.get('Project', '')), [])),
                                 reverse=False) :
        return True
    
    # 더 정교한 점수 계산 방식
    if try_enhanced_strategy(building_quantity.copy(), flexible_projects,
                             project_to_buildings, building_constraints) :
        return True
    
    # 몬테카를로 방식 시도 (5회)
    for _ in range(5) :
        if try_monte_carlo_strategy(building_quantity.copy(), flexible_projects,
                                    project_to_buildings, building_constraints) :
            return True
    
    return False # 모두 실패 했을 경우 false 반환

# 프로젝트를 여러 제조동에 분할 할당하는 함수
def try_distribution_with_splitting(building_quantity, flexible_projects, project_to_buildings, building_constraints):
    total_quantity = sum(building_quantity.values())
    
    # 물량이 큰 순서대로 정렬
    sorted_projects = sorted(flexible_projects, key=lambda x: x.get('MFG', 0), reverse=True)
    
    for item in sorted_projects:
        project = item.get('Basic2', item.get('Project', ''))
        quantity = item.get('MFG', 0)
        possible_buildings = project_to_buildings.get(project, [])
        
        if not possible_buildings:
            continue
            
        if len(possible_buildings) == 1:
            # 단일 제조동만 가능한 경우 전체 할당
            building_quantity[possible_buildings[0]] += quantity
            total_quantity += quantity
            continue
        
        # 현재 제조동별 비율 계산
        current_ratios = {b: qty / (total_quantity or 1) for b, qty in building_quantity.items()}
        
        # 최적 분할 비율 계산
        allocation_ratios = calculate_optimal_allocation_ratios(
            possible_buildings, current_ratios, building_constraints, building_quantity, total_quantity, quantity)
        
        # 계산된 비율로 분할 할당
        if allocation_ratios:
            for building, ratio in allocation_ratios.items():
                allocated_qty = quantity * ratio
                building_quantity[building] += allocated_qty
            
            total_quantity += quantity
    
    # 최종 비율 검증
    final_ratios = {b: qty / total_quantity for b, qty in building_quantity.items()} if total_quantity > 0 else {b: 0 for b in building_quantity}
    
    for building, ratio in final_ratios.items():
        if building not in building_constraints:
            continue
        
        lower = building_constraints[building]['lower_limit']
        upper = building_constraints[building]['upper_limit']
        
        if ratio < lower or ratio > upper:
            return False
    
    return True

# 제조동별 최적 할당 비율 계산
def calculate_optimal_allocation_ratios(possible_buildings, current_ratios, building_constraints, 
                                       building_quantity, total_quantity, project_quantity):
    # 각 제조동이 필요로 하는 물량 점수 계산
    building_scores = {}
    
    for building in possible_buildings:
        if building not in building_constraints:
            continue
        
        lower = building_constraints[building]['lower_limit']
        upper = building_constraints[building]['upper_limit']
        current = current_ratios.get(building, 0)
        
        if current < lower:
            gap = lower - current
            score = 10 + (20 * gap)
        elif current > upper:
            score = 0.1
        else:
            normalized_position = (current - lower) / (upper - lower)
            score = 5 * (1 - normalized_position)
        
        building_scores[building] = max(0.1, score)
    
    if not building_scores:
        return None
    
    # 점수를 기반으로 초기 비율 배분
    total_score = sum(building_scores.values())
    initial_ratios = {b: score / total_score for b, score in building_scores.items()}
    
    # 초기 비율 검증 및 최적화
    for _ in range(3):  # 3회 반복 최적화
        # 할당 후 제약조건 위반 여부 확인
        simulation_quantity = {b: q for b, q in building_quantity.items()}
        new_total = total_quantity
        
        for b, ratio in initial_ratios.items():
            allocated = project_quantity * ratio
            simulation_quantity[b] += allocated
        
        new_total += project_quantity
        simulated_ratios = {b: q / new_total for b, q in simulation_quantity.items()}
        
        violations = {}
        for b in building_constraints:
            if b not in simulated_ratios:
                continue
                
            lower = building_constraints[b]['lower_limit']
            upper = building_constraints[b]['upper_limit']
            sim_ratio = simulated_ratios[b]
            
            if sim_ratio < lower:
                violations[b] = {'type': 'below', 'gap': lower - sim_ratio}
            elif sim_ratio > upper:
                violations[b] = {'type': 'above', 'gap': sim_ratio - upper}
        
        if not violations:
            break
        
        # 비율 조정
        for b, v in violations.items():
            if b not in initial_ratios:
                continue
                
            if v['type'] == 'below':
                adjustment = min(0.1, v['gap'])
                available_buildings = [b2 for b2 in initial_ratios if b2 != b and b2 not in violations]
                
                if available_buildings:
                    decrement_per_building = adjustment / len(available_buildings)
                    initial_ratios[b] += adjustment
                    
                    for b2 in available_buildings:
                        initial_ratios[b2] = max(0.01, initial_ratios[b2] - decrement_per_building)
            
            elif v['type'] == 'above':
                adjustment = min(0.1, v['gap'])
                available_buildings = [b2 for b2 in initial_ratios if b2 != b and 
                                     (b2 not in violations or violations.get(b2, {}).get('type') == 'below')]
                
                if available_buildings:
                    increment_per_building = adjustment / len(available_buildings)
                    initial_ratios[b] = max(0.01, initial_ratios[b] - adjustment)
                    
                    for b2 in available_buildings:
                        initial_ratios[b2] += increment_per_building
        
        # 비율 정규화
        total = sum(initial_ratios.values())
        initial_ratios = {b: r / total for b, r in initial_ratios.items()}
    
    return initial_ratios

# 프로젝트마다 제조 가능한 제조동에 점수를 부여해 프로젝트 할당 (Greedy 함수)
def try_distribution_strategy(building_quantity, flexible_projects, project_to_buildings,
                              building_constraints, sort_key=None, reverse=False) :
    
    sorted_projects = sorted(flexible_projects, key=sort_key, reverse=reverse) if sort_key else flexible_projects
    total_quantity = sum(building_quantity.values())

    for item in sorted_projects :
        project = item.get('Basic2', item.get('Project', ''))
        quantity = item.get('MFG', 0)
        possible_buildings = project_to_buildings.get(project, [])

        if not possible_buildings :
            continue

        current_ratios = {b: qty / (total_quantity or 1) for b, qty in building_quantity.items()}

        building_scores = {}

        for building in possible_buildings :
            if building not in building_constraints :
                continue

            lower = building_constraints[building]['lower_limit']
            upper = building_constraints[building]['upper_limit']
            current = current_ratios[building]

            if current < lower :
                score = (lower - current) * 10
            elif current > upper :
                score = -10
            else :
                margin_above_lower = current - lower
                normalized_score = 1 - (margin_above_lower / (upper - lower))
                score = normalized_score * 5

            building_scores[building] = score

        if not building_scores :
            continue

        best_building = max(building_scores.keys(),
                            key = lambda b : building_scores[b])
        
        building_quantity[best_building] += quantity
        total_quantity += quantity

    final_ratios = {b: qty / total_quantity for b, qty in building_quantity.items()} if total_quantity > 0 else {b : 0 for b in building_quantity}

    for building, ratio in final_ratios.items() :
        if building not in building_constraints :
            continue

        lower = building_constraints[building]['lower_limit']
        upper = building_constraints[building]['upper_limit']

        if ratio < lower or ratio > upper :
            return False
        
    return True

# 우선순위 기반 할당(휴리스틱 알고리즘)
def try_enhanced_strategy(building_quantity, flexible_projects, project_to_buildings, building_constraints) :
    total_quantity = sum(building_quantity.values())
    initial_ratios = {b: qty / (total_quantity or 1) for b, qty in building_quantity.items()}

    priority_buildings = []

    for building, ratio in initial_ratios.items() :
        if building in building_constraints :
            lower = building_constraints[building]['lower_limit']
            upper = building_constraints[building]['upper_limit']

            if ratio < lower :
                priority_buildings.append((building, 'increase', lower - ratio))
            elif ratio > upper :
                priority_buildings.append((building, 'decrease', ratio - upper))

    priority_buildings.sort(key=lambda x : x[2], reverse=True)

    building_priority = {}

    for building in building_constraints :
        building_priority[building] = 0

    for building, direction, gap in priority_buildings :
        if direction == 'increase' :
            building_priority[building] = 10 * gap
        elif direction == 'decrease' :
            building_priority[building] = -10 * gap

    sorted_projects = sorted(flexible_projects, key=lambda x : x.get('MFG', 0), reverse=True)

    for item in sorted_projects :
        project = item.get('Basic2', item.get('Project', ''))
        quantity = item.get('MFG', 0)
        possible_buildings = project_to_buildings.get(project, [])

        if not possible_buildings :
            continue

        total_quantity = sum(building_quantity.values())
        current_ratios = {b: qty / (total_quantity or 1) for b, qty in building_quantity.items()}

        building_scores = {}

        for building in possible_buildings :
            if building not in building_constraints :
                continue

            lower = building_constraints[building]['lower_limit']
            upper = building_constraints[building]['upper_limit']
            current = current_ratios[building]

            base_priority = building_priority[building]

            if current < lower :
                gap_score = (lower - current) * 15
                score = base_priority + gap_score
            elif current > upper :
                gap_score = -(current - upper) * 15
                score = base_priority + gap_score
            else :
                margin = (current - lower) / (upper - lower)
                adjustment = (1 - margin) * 5
                score = base_priority + adjustment
            
            building_scores[building] = score

        if building_scores :
            best_building = max(building_scores.keys(), key = lambda b : building_scores[b])
            building_quantity[best_building] += quantity

        total_quantity = sum(building_quantity.values())
        updated_ratios = {b : qty / total_quantity for b, qty in building_quantity.items()}

        for building in building_priority :
            if building in building_constraints :
                lower = building_constraints[building]['lower_limit']
                upper = building_constraints[building]['upper_limit']
                current = updated_ratios[building]

                if current < lower :
                    building_priority[building] = 10 * (lower - current)
                elif current > upper :
                    building_priority[building] = -10 * (current - upper)
                else :
                    building_priority[building] = 0

    total_quantity = sum(building_quantity.values())
    final_ratios = {b : qty / total_quantity for b, qty in building_quantity.items()} if total_quantity > 0 else {b : 0 for b in building_quantity}

    for building, ratio in final_ratios.items() :
        if building not in building_constraints :
            continue

        lower = building_constraints[building]['lower_limit']
        upper = building_constraints[building]['upper_limit']

        if ratio < lower or ratio > upper :
            return False
        
    return True

# 몬테카를로(랜덤 분배) 방식 시도
def try_monte_carlo_strategy(building_quantity, flexible_projects, project_to_buildings, building_constraints) :
    total_quantity = sum(building_quantity.values())

    shuffled_projects = flexible_projects.copy()
    random.shuffle(shuffled_projects)

    for item in shuffled_projects :
        project = item.get('Basic2', item.get('Project', ''))
        quantity = item.get('MFG', 0)
        possible_buildings = project_to_buildings.get(project, [])

        if not possible_buildings :
            continue

        current_ratios = {b: qty / (total_quantity or 1) for b, qty in building_quantity.items()}

        weights = []
        valid_buildings = []

        for building in possible_buildings :
            if building not in building_constraints :
                continue

            valid_buildings.append(building)
            lower = building_constraints[building]['lower_limit']
            upper = building_constraints[building]['upper_limit']
            current = current_ratios[building]

            if current < lower :
                weights.append(3.0 + (lower - current) * 10)
            elif current > upper :
                weights.append(0.1)
            else :
                normalized_position = (current - lower) / (upper - lower)
                weights.append(2.0 * (1 - normalized_position))

        if not valid_buildings :
            continue

        if sum(weights) > 0 :
            norm_weights = [w / sum(weights) for w in weights]
            chosen_idx = random.choices(range(len(valid_buildings)), weights = norm_weights, k = 1)[0]
            chosen_building = valid_buildings[chosen_idx]

            building_quantity[chosen_building] += quantity
            total_quantity += quantity
        else :
            chosen_building = random.choice(valid_buildings)
            building_quantity[chosen_building] += quantity
            total_quantity += quantity

    final_ratios = {b : qty / total_quantity for b, qty in building_quantity.items()} if total_quantity > 0 else {b : 0 for b in building_quantity}

    for building, ratio in final_ratios.items() :
        if building not in building_constraints :
            continue

        lower = building_constraints[building]['lower_limit']
        upper = building_constraints[building]['upper_limit']

        if ratio < lower or ratio > upper :
            return False
        
    return True

# 몬테카를로 분할 할당 방식
def try_monte_carlo_with_splitting(building_quantity, flexible_projects, project_to_buildings, building_constraints):
    total_quantity = sum(building_quantity.values())
    
    # 물량 큰 순으로 정렬
    sorted_projects = sorted(flexible_projects, key=lambda x: x.get('MFG', 0), reverse=True)
    
    for item in sorted_projects:
        project = item.get('Basic2', item.get('Project', ''))
        quantity = item.get('MFG', 0)
        possible_buildings = project_to_buildings.get(project, [])
        
        if not possible_buildings or len(possible_buildings) <= 1:
            # 단일 제조동 프로젝트는 기존 방식으로 처리
            if possible_buildings:
                building_quantity[possible_buildings[0]] += quantity
                total_quantity += quantity
            continue
        
        # 분할 가능한 프로젝트
        valid_buildings = [b for b in possible_buildings if b in building_constraints]
        if not valid_buildings:
            continue
        
        # 랜덤 분할 시도
        best_allocation = None
        best_violation_score = float('inf')
        
        for _ in range(10):
            # 랜덤 할당 비율 생성
            random_weights = [random.uniform(0.1, 1.0) for _ in range(len(valid_buildings))]
            total_weight = sum(random_weights)
            random_ratios = {valid_buildings[i]: random_weights[i] / total_weight for i in range(len(valid_buildings))}
            
            # 시뮬레이션
            sim_quantity = {b: q for b, q in building_quantity.items()}
            for b, r in random_ratios.items():
                sim_quantity[b] += quantity * r
            
            sim_total = total_quantity + quantity
            sim_ratios = {b: q / sim_total for b, q in sim_quantity.items()}
            
            # 위반 정도 계산
            violation_score = 0
            for b in building_constraints:
                if b not in sim_ratios:
                    continue
                    
                lower = building_constraints[b]['lower_limit']
                upper = building_constraints[b]['upper_limit']
                ratio = sim_ratios[b]
                
                if ratio < lower:
                    violation_score += (lower - ratio) * 10
                elif ratio > upper:
                    violation_score += (ratio - upper) * 10
            
            # 더 나은 할당 발견 시 업데이트
            if violation_score < best_violation_score:
                best_violation_score = violation_score
                best_allocation = random_ratios
        
        # 최적 할당 적용
        if best_allocation:
            for building, ratio in best_allocation.items():
                building_quantity[building] += quantity * ratio
            
            total_quantity += quantity
    
    # 최종 검증
    final_ratios = {b: qty / total_quantity for b, qty in building_quantity.items()} if total_quantity > 0 else {b: 0 for b in building_quantity}
    
    for building, ratio in final_ratios.items():
        if building not in building_constraints:
            continue
        
        lower = building_constraints[building]['lower_limit']
        upper = building_constraints[building]['upper_limit']
        
        if ratio < lower or ratio > upper:
            return False
    
    return True