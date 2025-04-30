import pandas as pd
import pulp 
from pulp import LpStatus
# from app.utils.fileHandler import load_file
# from app.models.common.fileStore import FilePaths


class Optimization:
    def __init__(self):
        # 각 엑셀 파일의 모든 시트를 불러오기. 시트이름이 키, 데이터프레임이 값인 딕셔너리로 저장됨.
        
        self.demand_excel = pd.read_excel('ssafy_demand_0408.xlsx', sheet_name=None)
        self.master_excel = pd.read_excel('ssafy_master_0408.xlsx', sheet_name=None)
        self.dynamic_excel =  pd.read_excel('ssafy_dynamic_0408.xlsx', sheet_name=None)

        # self.demand_excel = load_file(FilePaths.get("demand_excel_file"))
        # self.master_excel = load_file(FilePaths.get("master_excel_file"))
        # self.dynamic_excel =  load_file(FilePaths.get("dynamic_excel_file"))

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
        # 아이템에 To_site 까지 포함해서 아이템의 단위로 설정 (출하 capa를 목적함수에 포함시키기 위함)
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

        # 결정 변수 x : 모델 m을 라인 l, 시프트 s에서 몇 개 생산할지의 딕셔너리
        x = pulp.LpVariable.dicts("produce", [(m, l, s) for m in items for (l, s) in line_shifts], lowBound=0, cat='Integer')

        # 문제 정의
        model = pulp.LpProblem("LineShift_Production_Scheduling", pulp.LpMaximize)
        
        # 목적함수: 총 생산량 최대화 (추후 지표 8가지를 최적화 하는 목적함수로 수정 예정)
        model += pulp.lpSum([x[(m, l, s)] for m in items for (l, s) in line_shifts])

        # 제약조건 1: 모델별 수요량 보다 적게 생산. 꼭 모든 수요를 만족시키지 않아도 됨. demand 시트와 관련됨. 
        for m in items:
            model += pulp.lpSum([x[(m, l, s)] for (l, s) in line_shifts]) <= demand[m]

        # 제약조건 2: 라인/시프트에서 생산 가능한 모델만 허용. line_available 시트와 관련됨.
        for (l, s) in line_shifts:
            for m in items:
                if m not in allowed_items.get((l, s), []):
                    model += x[(m, l, s)] == 0

        # 제약조건 3: 제조동별 물량 비중 상한/하한. capa_portion 시트와 관련됨.
        for (ids,row) in self.df_capa_portion.iterrows():
            model += (
               row['upper_limit'] * pulp.lpSum([x[(m, l, s)] for (m, l, s) in x]) >=
               pulp.lpSum([x[(m, l, s)] for (m, l, s) in x if l.startswith(row['name'])])
            )
            model += (
                pulp.lpSum([x[(m, l, s)] for (m, l, s) in x if l.startswith(row['name'])]) >=
                row['lower_limit'] * pulp.lpSum([x[(m, l, s)] for (m, l, s) in x])
            )

        # 제약조건 4: 각 라인/시프트 조합의 최대 생산량 제한. capa_qty 시트와 관련됨.
        for (l, s) in line_shifts:
            model += pulp.lpSum([x[(m, l, s)] for m in items]) <= capacity[(l, s)]
        
        # 제약조건 5: 각 (제조동 * 시프트) 별 가동가능한 최대 라인 수. capa_qty 시트와 관련됨. Max_line
        # 결정변수 y 추가. y 는 각 (라인 * 시프트) 를 키값으로, 그 (라인*시프트) 가 가동중이면 1, 아니면 0 을 value 값으로 갖는 pulp 딕셔너리
        y = pulp.LpVariable.dicts("line_shift_active", line_shifts, cat="Binary")
        # 특정 y[(l,s)] 가 1이면 그 (라인*시프트) 에서 생산되는 모델이 적어도 1개는 있다는 뜻.반대로 0이면 하나도 없다는 뜻.
        BIG_M = 10_000_000  # 충분히 큰 값. _ 는 오직 가독성을 위한 표현.
        for (l, s) in line_shifts:
            total_produced = pulp.lpSum(x[(m, l, s)] for m in items)
            model += total_produced <= BIG_M * y[(l, s)]
            model += total_produced >= 1 * y[(l, s)]  
            
        blocks = list(set(l[0] for l in self.line)) # 제조동 리스트 ['I','D','K','M']

        for b in blocks:
            for shift in self.time:
                series = self.df_capa_qty.loc[self.df_capa_qty['Line'] == f"Max_line_{b}", shift]
                max_line = int(series.values[0]) if pd.notna(series.values[0]) else 100
                model += pulp.lpSum(
                    y[(l, s)] for (l, s) in line_shifts if l.startswith(b) and s == shift
                ) <= max_line

        # 제약조건 6: 각 (제조동 * 시프트) 별 최대 생산 수량. capa_qty 시트와 관련됨. Max_qty
        for b in blocks:
            for shift in self.time:
                series = self.df_capa_qty.loc[self.df_capa_qty['Line'] == f"Max_qty_{b}", shift]
                max_qty = int(series.values[0]) if pd.notna(series.values[0]) else 10_000_000
                model += pulp.lpSum(
                    x[(m, l, s)] for m in items for (l, s) in line_shifts if l.startswith(b) and s == shift
                ) <= max_qty

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

        # 생산해야 하는 아이템들 리스트. 
        items = []
        # 아이템별 생산 수요량 딕셔너리. 
        demand = {}

        # pre_assign 을 fixed_option에 통합한 데이터프레임 만들기
        self.df_combined = self.df_fixed_option.copy()
        for idx , row in self.df_pre_assign.iterrows():
            for i in range(1,8):
                if pd.notna(row['Item'+str(i)]):
                    self.df_combined.loc[len(self.df_combined)] = [row['item'+str(i)],row['Line'],2*i+row['Shift']-2,row['Qty'+str(i)] if pd.notna(row['Qty'+str(i)]) else 'ALL']
        
        # 통합한 시트의 아이템들을 items 와 demand 에 추가
        for index, row in self.df_combined.iterrows():
            if pd.isna(row['Qty']):
                print(row['Fixed_Group']+' 아이템의 Qty 가 비어있습니다')
                continue
            elif row['Qty'] == 'ALL':
                items.append(row['Fixed_Group'])
                df_items =self.df_demand[self.df_demand['Item']==row['Fixed_Group']]
                qty = 0
                for index, value in df_items.iterrows():
                    qty += value['MFG']
                demand[row['Fixed_Group']] = qty
            else : # Qty 에 값이 있을 경우
                items.append(row['Fixed_Group'])
                demand[row['Fixed_Group']] = row['Qty']
                
        # 라인*시프트 별 Capa (최대 생산 가능량)
        capacity = {(l,s):int(self.df_capa_qty.loc[self.df_capa_qty['Line'] == l, s].values[0]) for (l, s) in line_shifts}


        # 라인*시프트 별 생산가능 아이템. pre_assign, fixed_option 시트의 조건들이 들어가야함.
        allowed_items = {}
        fixed_line_shifts = {}
        for idx, row in self.df_combined.iterrows():
            fixed_lines = row['Fixed_Line'].split(",") if pd.notna(row['Fixed_Line']) else self.line
            fixed_times = list(map(int,str(row['Fixed_Time']).split(","))) if pd.notna(row['Fixed_Time']) else self.time
            fixed_line_shifts[row['Fixed_Group']] = [(line,time) for line in fixed_lines for time in fixed_times]
        print('fixed_line_shifts : ',fixed_line_shifts)
        # allowed_items_fixed = {(l,s):[] for (l,s) in line_shifts}
        # for idx, row in self.df_combined.iterrows():
        #     for line in row['Fixed_Line'].split(","):
        #         for time in row['Fixed_Time'].split(","):
        #             allowed_items_fixed[(line,time)].append(row['Fixed_Group'])
        fixed_items = self.df_combined['Fixed_Group'].to_list()

        print('fixed_items : ',fixed_items)
        for l, s in line_shifts:
            if l not in self.df_line_available.columns:
                raise ValueError(f"라인 {l}는 line_available에 존재하지 않습니다.")
            projects = self.df_line_available[self.df_line_available[l] == 1]['Project'].tolist()
            # 특정 라인*시프트에서는 특정 프로젝트의 모델만 생산 가능하고,그 모델은 사전할당에서 지정한 라인*시프트 범위 내여야 한다
            allowed = [m for m in items if any(m[3:7] == project for project in projects) ] #and ((l,s) in fixed_line_shifts[m])
            allowed_items[(l, s)] = allowed
        print('allowed_items : ',allowed_items)
        # 결정 변수: 모델 m을 라인 l, 시프트 s에서 몇 개 생산할지. 카테고리는 정수형.
        x = pulp.LpVariable.dicts("produce", [(m, l, s) for m in items for (l, s) in line_shifts], lowBound=0, cat='Integer')

        # 문제 정의. 최대화 문제
        model = pulp.LpProblem("LineShift_Production_Scheduling", pulp.LpMaximize)
        
        # 목적함수: 총 생산량 최대화
        model += pulp.lpSum([x[(m, l, s)] for m in items for (l, s) in line_shifts])
 
        # 제약조건 1: 모델별 총 수요량 충족 + 사전할당 알고리즘에서 모든 아이템은 무조건 할당되어야함
        # 모두 할당되는 경우가 없다면 사전할당이 애초에 불가능해야함.
        # 따라서 사전할당으로 주어진 아이템들을 모두 할당하는 경우만 가능한 해로 인정. 아래의 == 이 이런 의미.
        for m in items:
            model += pulp.lpSum([x[(m, l, s)] for (l, s) in line_shifts]) == demand[m]

        # 제약조건 2: 라인/시프트에서 생산 가능한 모델만 허용
        for (l, s) in line_shifts:
            for m in items:
                if m not in allowed_items.get((l, s), []):
                    model += x[(m, l, s)] == 0

        # 제약조건 3: 제조동별 물량 비중 상한/하한 (사전 할당에서는 고려할 필요 없다는 판단 하에 제약조건 제외)

        # 제약조건 4: 각 라인/시프트 조합의 최대 생산량 제한
        for (l, s) in line_shifts:
            model += pulp.lpSum([x[(m, l, s)] for m in items]) <= capacity[(l, s)]

        # 제약조건 5: 각 (제조동 * 시프트) 별 가동가능한 최대 라인 수. capa_qty 시트와 관련됨. Max_line
        # y 는 각 (라인 * 시프트) 를 키값으로, 그 (라인*시프트) 가 가동중이면 1, 아니면 0 을 value 값으로 갖는 pulp 딕셔너리
        y = pulp.LpVariable.dicts("line_shift_active", line_shifts, cat="Binary")
        # 특정 y[(l,s)] 가 1이면 그 (라인*시프트) 에서 생산되는 모델이 적어도 1개는 있다는 뜻.반대로 0이면 하나도 없다는 뜻.
        BIG_M = 10_000_000  # 충분히 큰 값. _ 는 오직 가독성을 위한 표현.
        for (l, s) in line_shifts:
            total_produced = pulp.lpSum(x[(m, l, s)] for m in items)
            model += total_produced <= BIG_M * y[(l, s)]
            model += total_produced >= 1 * y[(l, s)]  
            
        blocks = list(set(l[0] for l in self.line)) # 제조동 리스트 ['I','D','K','M']

        for b in blocks:
            for shift in self.time:
                series = self.df_capa_qty.loc[self.df_capa_qty['Line'] == f"Max_line_{b}", shift]
                max_line = int(series.values[0]) if pd.notna(series.values[0]) else 100
                model += pulp.lpSum(
                    y[(l, s)] for (l, s) in line_shifts if l.startswith(b) and s == shift
                ) <= max_line

        # 제약조건 6: 각 (제조동 * 시프트) 별 최대 생산 수량. capa_qty 시트와 관련됨. Max_qty
        for b in blocks:
            for shift in self.time:
                series = self.df_capa_qty.loc[self.df_capa_qty['Line'] == f"Max_qty_{b}", shift]
                max_qty = int(series.values[0]) if pd.notna(series.values[0]) else 10_000_000
                model += pulp.lpSum(
                    x[(m, l, s)] for m in items for (l, s) in line_shifts if l.startswith(b) and s == shift
                ) <= max_qty

        # 최적화
        model.solve()

        # 결과 저장 & 출력
        results = []
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
        if LpStatus[model.status] == 'Optimal':
            print(f"\n총 생산량: {int(pulp.value(model.objective))}개")
        else:
            print("❌ 최적해를 찾지 못했습니다. (status =", LpStatus[model.status], ")")
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
    optimization.pre_assign()
