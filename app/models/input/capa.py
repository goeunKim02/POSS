import pandas as pd
from app.utils.fileHandler import load_file
from app.models.common.fileStore import FilePaths

def process_data():
    master_file_path = FilePaths.get("master_excel_file")
    dynamic_file_path = FilePaths.get("dynamic_excel_file")
    demand_file_path = FilePaths.get("demand_excel_file")
    etc_file_path = FilePaths.get("etc_excel_file")

    if demand_file_path:
        df_demand = load_file(demand_file_path)
        df_demand_demand = df_demand.get('demand', pd.DataFrame())  # demand 파일의 demand 시트

        for i, row in df_demand_demand.iterrows():
            df_demand_demand.loc[i, "Project"] = row['Item'][3:7]
            df_demand_demand.loc[i, "Basic2"] = row['Item'][3:8]
            df_demand_demand.loc[i, "Tosite_group"] = row['Item'][7:8]
            df_demand_demand.loc[i, "RMC"] = row['Item'][3:-3]
            df_demand_demand.loc[i, "Color"] = row['Item'][8:-4]

    if dynamic_file_path:
        df_dynamic = load_file(dynamic_file_path)

    if master_file_path:
        df_master = load_file(master_file_path)
        df_master_line_available = df_master.get('line_available', pd.DataFrame()) # master 파일의 line_available 시트
        df_master_capa_portion = df_master.get('capa_portion', pd.DataFrame()) # master 파일의 capa_portion 시트
        df_master_capa_qty = df_master.get('capa_qty', pd.DataFrame()) # master 파일의 capa_qty 시트

        if demand_file_path:
            time = {i for i in df_master_capa_qty.columns}
            line = df_master_line_available.columns
            item = df_demand_demand.index.tolist()
            project = df_demand_demand["Basic2"].unique()

    if etc_file_path:
        df_etc = load_file(etc_file_path)

    if (demand_file_path and master_file_path
        and not df_demand_demand.empty and not df_master_line_available.empty
        and not df_master_capa_qty.empty and not df_master_capa_portion.empty) :

        processed_data = preprocess_data(df_demand_demand, df_master_line_available, df_master_capa_qty, df_master_capa_portion)

        return processed_data
    else :
        print("필요한 데이터 파일 또는 시트가 누락 되었습니다")
        return None
    
# 이상치 분석을 위한 데이터 전처리
def preprocess_data(df_demand, df_line_available, df_capa_qty, df_capa_portion):
    processed_data = {
        'demand_items': [],
        'project_to_buildings': {},
        'line_capacities': {},
        'building_constraints': {}
    }

    # 제조동 목록
    buildings = []

    if not df_capa_portion.empty:
        if 'name' in df_capa_portion.columns:
            buildings = df_capa_portion['name'].tolist()
        else:
            buildings = [col for col in df_capa_portion.columns if col != 'name']

    for _, row in df_demand.iterrows():
        item = row.to_dict()
        processed_data['demand_items'].append(item)

    for _, row in df_line_available.iterrows() :
        project = row['Project'] if 'Project' in row else row.name
        project_buildings = []

        for building in buildings :
            building_columns = [col for col in row.index if col.startswith(f"{building}_")]

            if any(row[col] == 1 for col in building_columns if pd.notna(row[col])) :
                project_buildings.append(building)

        if 'Basic2' in df_demand.columns :
            for basic2 in df_demand['Basic2'].unique() :
                if basic2.startswith(project) :
                    processed_data['project_to_buildings'][basic2] = project_buildings

        else :
            processed_data['project_to_buildings'][project] = project_buildings
    
    # 라인 생산 용량
    for _, row in df_capa_qty.iterrows() :
        if 'Line' in row and 'Capacity' in row :
            line_id = row['Line']
            capacity = row['Capacity']
            processed_data['line_capacities'][line_id] = capacity

    # 제조동 제약 조건
    for _, row in df_capa_portion.iterrows() :
        if 'name' in row and 'lower_limit' in row and 'upper_limit' in row :
            building = row['name']
            processed_data['building_constraints'][building] = {
                'lower_limit' : float(row['lower_limit']),
                'upper_limit' : float(row['upper_limit'])
            }

    return processed_data