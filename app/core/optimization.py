import pandas as pd
import pulp 
from app.utils.fileHandler import load_file
from app.models.common.fileStore import FilePaths


class Optimization:
    def __init__(self):
        # 각 엑셀 파일의 모든 시트를 불러오기. 시트이름이 키, 데이터프레임이 값인 딕셔너리로 저장됨.
        
        # self.demand_excel = pd.read_excel('ssafy_demand_0408.xlsx', sheet_name=None)
        # self.master_excel = pd.read_excel('ssafy_master_0408.xlsx', sheet_name=None)
        # self.dynamic_excel =  pd.read_excel('ssafy_dynamic_0408.xlsx', sheet_name=None)

        self.demand_excel = load_file(FilePaths.get("demand_excel_file"))
        self.master_excel = load_file(FilePaths.get("master_excel_file"))
        self.dynamic_excel =  load_file(FilePaths.get("dynamic_excel_file"))
        print(self.demand_excel['demand'].head())

        # demand 엑셀 파일의 시트를 데이터프레임으로 만들고 주로 쓰일 변수도 정의
        self.df_demand = self.demand_excel['demand'] 
        for i, row in self.df_demand.iterrows() :    
            self.df_demand.loc[i, "Project"] = row["Item"][3:7]
            self.df_demand.loc[i, "Basic2"] = row['Item'][3:8]
            self.df_demand.loc[i, "Tosite_group"] = row["Item"][7:8]
            self.df_demand.loc[i, "RMC"] = row['Item'][3:-3]
            self.df_demand.loc[i, "Color"] = row['Item'][8:-4]

        self.item = self.df_demand.index.tolist()
        self.project = self.df_demand["Basic2"].unique()
        self.RMC = self.df_demand.RMC.unique()

        # master 엑셀 파일의 시트들을 데이터프레임으로 만들고 주로 쓰일 변수도 정의
        self.df_capa_portion = self.master_excel['capa_portion']
        self.df_capa_qty = self.master_excel['capa_qty']
        self.df_line_available = self.master_excel['line_available']
        self.df_capa_outgoing = self.master_excel['capa_outgoing']
        self.df_capa_imprinter = self.master_excel['capa_imprinter']
        self.df_due_LT = self.master_excel['due_LT']

        self.time = {i for i in self.df_capa_qty.columns}
        self.line = self.df_line_available.columns
        self.port_list = self.df_capa_outgoing.Tosite_port.unique()
        self.day_list = list(reversed(range(1, 8)))

        # dynamic 엑셀 파일의 시트들을 데이터프레임으로 만들고 주로 쓰일 변수도 정의
        self.df_material_item = self.dynamic_excel['material_item']
        self.df_material_qty = self.dynamic_excel['material_qty']
        self.df_material_equal = self.dynamic_excel['material_equal']
        self.df_due_request = self.dynamic_excel['due_request']
        self.df_pre_assign = self.dynamic_excel['pre_assign']
        self.df_fixed_option = self.dynamic_excel['fixed_option']

        # 리스트로 쓰는게 편해서 리스트로 변환
        self.time = self.time.difference({'Line'})
        self.time = list(range(1,15))
        self.line = self.line.to_list()[1:]

    # 생산계획 최적화 함수(할당은 되지만 아직 미완성)
    def execute(self):
        items = (self.df_demand['Item'] + self.df_demand['To_Site']).tolist()
        lines = self.line
        shifts = self.time
        line_shifts = [(l,s) for l in lines for s in shifts]
        demand = dict(zip(self.df_demand['Item']+self.df_demand['To_Site'], self.df_demand['MFG']))
        capacity = {(l,s):int(self.df_capa_qty.loc[self.df_capa_qty['Line'] == l, s].values[0]) for (l, s) in line_shifts}

        allowed_items = {}
        for l, s in line_shifts:
            if l not in self.df_line_available.columns:
                raise ValueError(f"라인 {l}는 line_available에 존재하지 않습니다.")
            # line_available에서 값이 1 인 프로젝트들의 리스트
            projects = self.df_line_available[self.df_line_available[l] == 1]['Project'].tolist()
            allowed = [m for m in items if any(m[3:7] == project for project in projects)]
            allowed_items[(l, s)] = allowed

        # 결정 변수: 모델 m을 라인 l, 시프트 s에서 몇 개 생산할지
        x = pulp.LpVariable.dicts("produce", [(m, l, s) for m in items for (l, s) in line_shifts], lowBound=0, cat='Integer')

        # 문제 정의
        model = pulp.LpProblem("LineShift_Production_Scheduling", pulp.LpMaximize)
        
        # 목적함수: 총 생산량 최대화 (추후 지표 8가지를 최적화 하는 목적함수로 수정 예정)
        model += pulp.lpSum([x[(m, l, s)] for m in items for (l, s) in line_shifts])

        # 제약조건 1: 각 라인/시프트 조합의 최대 생산량 제한
        for (l, s) in line_shifts:
            model += pulp.lpSum([x[(m, l, s)] for m in items]) <= capacity[(l, s)]

        # 제약조건 2: 모델별 총 수요량 충족
        for m in items:
            model += pulp.lpSum([x[(m, l, s)] for (l, s) in line_shifts]) <= demand[m]

        # 제약조건 3: 라인/시프트에서 생산 가능한 모델만 허용
        for (l, s) in line_shifts:
            for m in items:
                if m not in allowed_items.get((l, s), []):
                    model += x[(m, l, s)] == 0
        
        # 제약조건 4: 제조동별 물량 비중 상한/하한
        for (ids,row) in self.df_capa_portion.iterrows():
            model += (
               row['upper_limit'] * pulp.lpSum([x[(m, l, s)] for (m, l, s) in x]) >=
               pulp.lpSum([x[(m, l, s)] for (m, l, s) in x if l.startswith(row['name'])])
            )
            model += (
                pulp.lpSum([x[(m, l, s)] for (m, l, s) in x if l.startswith(row['name'])]) >=
                row['lower_limit'] * pulp.lpSum([x[(m, l, s)] for (m, l, s) in x])
            )

        # 최적화
        model.solve()

        # 결과 출력
        results = []
        for (l, s) in line_shifts:
            print(f"{l} - {s} 시프트:")
            for m in items:
                units = int(pulp.value(x[(m, l, s)]))
                if units > 0:
                    print(f"  모델 {m} → {units}개 생산")
                    # 아이템의 SOP 와 MFG 값은 demand 시트에서 참조, due_LT 값은 due_LT 시트에서 참조
                    sop = self.df_demand.loc[(self.df_demand['Item']==m[:-2])&(self.df_demand['To_Site']==m[-2:]),'SOP'].values[0]
                    mfg = self.df_demand.loc[(self.df_demand['Item']==m[:-2])&(self.df_demand['To_Site']==m[-2:]),'MFG'].values[0]
                    due_lt= self.df_due_LT.loc[(self.df_due_LT['Project']==m[3:7])&(self.df_due_LT['Tosite_group']==m[7:8]),'Due_date_LT'].values[0]
                    results.append((l,s,m,m[:-2],units,m[3:7],m[-2:],sop,mfg,m[3:11],due_lt)) 
        print(f"\n총 생산량: {int(pulp.value(model.objective))}개")
        # 제조동별 생산량
        total_production = pulp.value(pulp.lpSum([x[(m, l, s)] for (m, l, s) in x]))
        for (idx,row) in self.df_capa_portion.iterrows():
            line_production =pulp.value(pulp.lpSum([x[(m, l, s)] for (m, l, s) in x if l.startswith(row['name'])]))
            line_ratio = (line_production / total_production) * 100 if total_production != 0 else 0
            print(f"{row['name']}라인 생산량: {int(line_production)}개, {row['name']}라인 비중: {line_ratio:.2f}%")

        df_result = pd.DataFrame(results,columns=['Line','Time','Demand','Item','Qty','Project','To_site','SOP','MFG','RMC','Due_LT'])
        df_result.to_excel('assign_result.xlsx',index = False)
    
    # 사전할당 알고리즘 함수(이것도 미완성)
    def pre_assign(self):
        lines = self.line
        shifts = self.time

        # 모든 (line * shift) 를 원소로 하는 리스트
        line_shifts = [(l,s) for l in lines for s in shifts]

        # 생산해야 하는 아이템들 리스트. pre_assign, fixed_option 시트의 아이템들만
        items = []

        # 아이템별 생산 수요량 딕셔너리. pre_assign, fixed_option 시트의 아이템들만
        demand = {}
        
        # fixed_option 시트의 아이템들을 items 와 demand 에 추가(pre_assign 시트는 추후 구현 예정)
        for index, row in self.df_fixed_option.iterrows():
            fixed_group = row['Fixed_Group']
            df_items =self.df_demand[self.df_demand['Item']==fixed_group]
            for index, value in df_items.iterrows():
                item = value['Item']
                to_site = value['To_Site']
                items.append(item+to_site)
                demand[item+to_site] = value['MFG']
                
        # 라인*시프트 별 Capa (최대 생산 가능량)
        capacity = {(l,s):int(self.df_capa_qty.loc[self.df_capa_qty['Line'] == l, s].values[0]) for (l, s) in line_shifts}


        # 라인*시프트 별 생산가능 아이템. pre_assign, fixed_option 시트의 조건들이 들어가야함. (pre_assign은 추후 추가)
        allowed_items = {}
        fixed_items = self.df_fixed_option['Fixed_Group'].to_list()
        print(fixed_items)
        for l, s in line_shifts:
            if l not in self.df_line_available.columns:
                raise ValueError(f"라인 {l}는 line_available에 존재하지 않습니다.")
            projects = self.df_line_available[self.df_line_available[l] == 1]['Project'].tolist()
            allowed = [m for m in items if any(m[3:7] == project for project in projects)]
            allowed_items[(l, s)] = allowed

        # 결정 변수: 모델 m을 라인 l, 시프트 s에서 몇 개 생산할지. 카테고리는 정수형.
        x = pulp.LpVariable.dicts("produce", [(m, l, s) for m in items for (l, s) in line_shifts], lowBound=0, cat='Integer')

        # 문제 정의. 최대화 문제
        model = pulp.LpProblem("LineShift_Production_Scheduling", pulp.LpMaximize)
        
        # 목적함수: 총 생산량 최대화 (예시)
        model += pulp.lpSum([x[(m, l, s)] for m in items for (l, s) in line_shifts])

        # 제약조건 1: 각 라인/시프트 조합의 최대 생산량 제한
        for (l, s) in line_shifts:
            model += pulp.lpSum([x[(m, l, s)] for m in items]) <= capacity[(l, s)]

        # 제약조건 2: 모델별 총 수요량 충족
        for m in items:
            model += pulp.lpSum([x[(m, l, s)] for (l, s) in line_shifts]) <= demand[m]

        # 제약조건 3: 라인/시프트에서 생산 가능한 모델만 허용
        for (l, s) in line_shifts:
            for m in items:
                if m not in allowed_items.get((l, s), []):
                    model += x[(m, l, s)] == 0

        # 제약조건 4: 제조동별 물량 비중 상한/하한 (임시로 빼둠)
        # for (ids,row) in self.df_capa_portion.iterrows():
        #     model += (
        #        row['upper_limit'] * pulp.lpSum([x[(m, l, s)] for (m, l, s) in x]) >=
        #        pulp.lpSum([x[(m, l, s)] for (m, l, s) in x if l.startswith(row['name'])])
        #     )
        #     model += (
        #         pulp.lpSum([x[(m, l, s)] for (m, l, s) in x if l.startswith(row['name'])]) >=
        #         row['lower_limit'] * pulp.lpSum([x[(m, l, s)] for (m, l, s) in x])
        #     )

        # 최적화
        model.solve()

        results = []

        # 결과 저장 & 출력
        for (l, s) in line_shifts:
            print(f"\n{l} - {s} 시프트:")
            for m in items:
                units = int(pulp.value(x[(m, l, s)]))
                if units > 0:
                    print(f"  모델 {m} → {units}개 생산")
                    
                    # 아이템의 SOP 와 MFG 값은 demand 시트에서 참조, due_LT 값은 due_LT 시트에서 참조
                    sop = self.df_demand.loc[(self.df_demand['Item']==m[:-2])&(self.df_demand['To_Site']==m[-2:]),'SOP'].values[0]
                    mfg = self.df_demand.loc[(self.df_demand['Item']==m[:-2])&(self.df_demand['To_Site']==m[-2:]),'MFG'].values[0]
                    due_lt= self.df_due_LT.loc[(self.df_due_LT['Project']==m[3:7])&(self.df_due_LT['Tosite_group']==m[7:8]),'Due_date_LT'].values[0]
                    results.append((l,s,m,m[:-2],units,m[3:7],m[-2:],sop,mfg,m[3:11],due_lt)) 

        print(f"\n총 생산량: {int(pulp.value(model.objective))}개")
        # 제조동별 생산량
        total_production = pulp.value(pulp.lpSum([x[(m, l, s)] for (m, l, s) in x]))
        for (idx,row) in self.df_capa_portion.iterrows():
            line_production =pulp.value(pulp.lpSum([x[(m, l, s)] for (m, l, s) in x if l.startswith(row['name'])]))
            line_ratio = (line_production / total_production) * 100 if total_production != 0 else 0
            print(f"{row['name']}라인 생산량: {int(line_production)}개, {row['name']}라인 비중: {line_ratio:.2f}%")

        df_result = pd.DataFrame(results,columns=['Line','Time','Demand','Item','Qty','Project','To_site','SOP','MFG','RMC','Due_LT'])
        return df_result

if __name__ == "__main__":
    optimization = Optimization()
    optimization.execute()
