import pulp

# 모델과 시프트
models = ['A', 'B', 'C']
shifts = ['S1', 'S2', 'S3']

# 각 모델별 생산 목표량
demand = {'A': 6, 'B': 4, 'C': 3}

# 각 시프트당 생산 가능 총 수량
shift_capacity = {'S1': 5, 'S2': 5, 'S3': 5}

# 시프트별로 생산 가능한 모델 목록
shift_model_capacity = {
    'S1': ['A', 'B'],
    'S2': ['B', 'C'],
    'S3': ['A', 'C']
}

# 결정 변수: 모델 m을 시프트 s에서 생산하는 수량
x = pulp.LpVariable.dicts("produce", [(m, s) for m in models for s in shifts], lowBound=0, cat='Integer')

# 문제 정의
model = pulp.LpProblem("Production_Scheduling", pulp.LpMinimize)

# 목적함수: 인건비 또는 총 생산량을 최소화
model += pulp.lpSum([x[(m, s)] for m in models for s in shifts])

# 제약조건 1: 시프트별 최대 생산량 제한
for s in shifts:
    model += pulp.lpSum([x[(m, s)] for m in models]) <= shift_capacity[s]

# 제약조건 2: 모델별 생산 목표 충족
for m in models:
    model += pulp.lpSum([x[(m, s)] for s in shifts]) >= demand[m]

# 제약조건 3: 시프트별로 생산 가능한 모델 제한
for s in shifts:
    for m in models:
        if m not in shift_model_capacity[s]:  # 해당 시프트에서는 이 모델을 생산할 수 없음
            model += x[(m, s)] == 0

# 풀기
model.solve()

# 출력
for s in shifts:
    print(f"\n{s} 시프트:")
    for m in models:
        units = int(pulp.value(x[(m, s)]))
        if units > 0:
            print(f"  모델 {m} → {units}개 생산")

print(f"\n총 생산량: {int(pulp.value(model.objective))}개")
