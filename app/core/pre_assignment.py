import pandas as pd
import pulp 

class Optimization:
    df_demand = pd.read_excel('ssafy_demand_0408.xlsx', sheet_name="demand")
    for i, row in df_demand.iterrows() :    
        df_demand.loc[i, "Project"] = row["Item"][3:7]
        df_demand.loc[i, "Basic2"] = row['Item'][3:8]
        df_demand.loc[i, "Tosite_group"] = row["Item"][7:8]
        df_demand.loc[i, "RMC"] = row['Item'][3:-3]
        df_demand.loc[i, "Color"] = row['Item'][8:-4]
    item = df_demand.index.tolist()
    project = df_demand["Basic2"].unique()
    RMC = df_demand.RMC.unique()

    df_capa_portion = pd.read_excel('ssafy_master_0408.xlsx',sheet_name='capa_portion')
    df_capa_qty = pd.read_excel('ssafy_master_0408.xlsx', sheet_name="capa_qty")
    df_line_available = pd.read_excel('ssafy_master_0408.xlsx', sheet_name="line_available")
    df_capa_outgoing = pd.read_excel('ssafy_master_0408.xlsx',sheet_name="capa_outgoing")
    df_capa_imprinter = pd.read_excel('ssafy_master_0408.xlsx',sheet_name="capa_imprinter")
    df_due_LT = pd.read_excel('ssafy_master_0408.xlsx',sheet_name="due_LT")
    time = {i for i in df_capa_qty.columns}
    line = df_line_available.columns
    port_list = df_capa_outgoing.Tosite_port.unique()
    day_list = list(reversed(range(1, 8)))

    df_material_item = pd.read_excel('ssafy_dynamic_0408.xlsx',sheet_name='material_item')
    df_material_qty = pd.read_excel('ssafy_dynamic_0408.xlsx',sheet_name='material_qty')
    df_material_equal = pd.read_excel('ssafy_dynamic_0408.xlsx',sheet_name='material_equal')
    df_due_request = pd.read_excel('ssafy_dynamic_0408.xlsx',sheet_name='due_request')
    df_pre_assign = pd.read_excel('ssafy_dynamic_0408.xlsx',sheet_name='pre_assign')
    df_fixed_option = pd.read_excel('ssafy_dynamic_0408.xlsx',sheet_name='fixed_option')

    time = time.difference({'Line'})
    time = list(range(1,15))
    line = line.to_list()[1:]

    # 생산계획 최적화 함수
    def execute(self):
        models = (self.df_demand['Item'] + self.df_demand['To_Site']).tolist()
        lines = self.line
        shifts = self.time
        line_shifts = [(l,s) for l in lines for s in shifts]
        demand = dict(zip(self.df_demand['Item']+self.df_demand['To_Site'], self.df_demand['MFG']))
        capacity = {(l,s):int(self.df_capa_qty.loc[self.df_capa_qty['Line'] == l, s].values[0]) for (l, s) in line_shifts}


        allowed_models = {}
        print(models)
        for l, s in line_shifts:
            if l not in self.df_line_available.columns:
                raise ValueError(f"라인 {l}는 line_available에 존재하지 않습니다.")
            # line_available에서 해당 열(l)이 1인 모델 ID (index) 추출
            projects = self.df_line_available[self.df_line_available[l] == 1]['Project'].tolist()
            allowed = [m for m in models if any(m[3:7] == project for project in projects)]
            allowed_models[(l, s)] = allowed

        # 결정 변수: 모델 m을 라인 l, 시프트 s에서 몇 개 생산할지
        x = pulp.LpVariable.dicts("produce", [(m, l, s) for m in models for (l, s) in line_shifts], lowBound=0, cat='Integer')

        # 문제 정의
        model = pulp.LpProblem("LineShift_Production_Scheduling", pulp.LpMaximize)
        
        # 목적함수: 총 생산량 최대화 (예시)
        model += pulp.lpSum([x[(m, l, s)] for m in models for (l, s) in line_shifts])

        # 제약조건 1: 각 라인/시프트 조합의 최대 생산량 제한
        for (l, s) in line_shifts:
            model += pulp.lpSum([x[(m, l, s)] for m in models]) <= capacity[(l, s)]

        # 제약조건 2: 모델별 총 수요량 충족
        for m in models:
            model += pulp.lpSum([x[(m, l, s)] for (l, s) in line_shifts]) <= demand[m]

        # 제약조건 3: 라인/시프트에서 생산 가능한 모델만 허용
        for (l, s) in line_shifts:
            for m in models:
                if m not in allowed_models.get((l, s), []):
                    model += x[(m, l, s)] == 0

        # 최적화
        model.solve()

        # 결과 출력
        for (l, s) in line_shifts:
            print(f"\n{l} - {s} 시프트:")
            for m in models:
                units = int(pulp.value(x[(m, l, s)]))
                if units > 0:
                    print(f"  모델 {m} → {units}개 생산")
        print(f"\n총 생산량: {int(pulp.value(model.objective))}개")

    def pre_assign(self):
        models = []
        lines = self.line
        shifts = self.time
        line_shifts = [(l,s) for l in lines for s in shifts]
        # demand = dict(zip(self.df_demand['Item']+self.df_demand['To_Site'], self.df_demand['MFG']))
        # demand 에 pre_assign 의 아이템들만 들어가야함
        demand = {}
        for index, row in self.df_fixed_option.iterrows():
            fixed_group = row['Fixed_Group']
            df_items =self.df_demand[self.df_demand['Item']==fixed_group]
            for index, value in df_items.iterrows():
                item = value['Item']
                to_site = value['To_Site']
                models.append(item+to_site)
                demand[item+to_site] = value['MFG']
        # for index, row in self.df_fixed_option.iterrows():
        capacity = {(l,s):int(self.df_capa_qty.loc[self.df_capa_qty['Line'] == l, s].values[0]) for (l, s) in line_shifts}


        # allowed models 에 pre_assign 의 조건들이 들어가야함
        allowed_models = {}
        fixed_items = self.df_fixed_option['Fixed_Group'].to_list()
        print(fixed_items)
        for l, s in line_shifts:
            if l not in self.df_line_available.columns:
                raise ValueError(f"라인 {l}는 line_available에 존재하지 않습니다.")
            projects = self.df_line_available[self.df_line_available[l] == 1]['Project'].tolist()
            allowed = [m for m in models if any(m[3:7] == project for project in projects) and m not in fixed_items]
            allowed_models[(l, s)] = allowed

        # 결정 변수: 모델 m을 라인 l, 시프트 s에서 몇 개 생산할지
        x = pulp.LpVariable.dicts("produce", [(m, l, s) for m in models for (l, s) in line_shifts], lowBound=0, cat='Integer')

        # 문제 정의
        model = pulp.LpProblem("LineShift_Production_Scheduling", pulp.LpMaximize)
        
        # 목적함수: 총 생산량 최대화 (예시)
        model += pulp.lpSum([x[(m, l, s)] for m in models for (l, s) in line_shifts])

        # 제약조건 1: 각 라인/시프트 조합의 최대 생산량 제한
        for (l, s) in line_shifts:
            model += pulp.lpSum([x[(m, l, s)] for m in models]) <= capacity[(l, s)]

        # 제약조건 2: 모델별 총 수요량 충족
        for m in models:
            model += pulp.lpSum([x[(m, l, s)] for (l, s) in line_shifts]) <= demand[m]

        # 제약조건 3: 라인/시프트에서 생산 가능한 모델만 허용
        for (l, s) in line_shifts:
            for m in models:
                if m not in allowed_models.get((l, s), []):
                    model += x[(m, l, s)] == 0

        # 최적화
        model.solve()

        # 결과 출력
        for (l, s) in line_shifts:
            print(f"\n{l} - {s} 시프트:")
            for m in models:
                units = int(pulp.value(x[(m, l, s)]))
                if units > 0:
                    print(f"  모델 {m} → {units}개 생산")
        print(f"\n총 생산량: {int(pulp.value(model.objective))}개")
    def tmp_print(self):
        demand = {}
        for index, row in self.df_fixed_option.iterrows():
            fixed_group = row['Fixed_Group']
            df_items =self.df_demand[self.df_demand['Item']==fixed_group]
            for index, value in df_items.iterrows():
                item = value['Item']
                to_site = value['To_Site']
                demand[item+to_site] = value['MFG']
        print(demand)
if __name__ == "__main__":
    optimization = Optimization()
    optimization.pre_assign()
