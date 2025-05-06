import pandas as pd
from app.models.common.fileStore import FilePaths
from app.utils.fileHandler import load_file

"""
당주 출하 만족률 계산을 위한 전처리
"""
def preprocess_data_for_fulfillment_rate() :
    master_file_path = FilePaths.get('master_excel_file')
    material_file_path = FilePaths.get('dynamic_excel_file')
    demand_file_path = FilePaths.get('demand_excel_file')

    master_data = load_file(master_file_path)
    material_data = load_file(material_file_path)
    demand_data = load_file(demand_file_path)

    df_demand = demand_data.get('demand', pd.DataFrame())
    df_due_lt = master_data.get('due_LT', pd.DataFrame())
    df_line_available = master_data.get('line_available', pd.DataFrame())
    df_capa_qty = master_data.get('capa_qty', pd.DataFrame())
    df_material_qty = material_data.get('material_qty', pd.DataFrame())
    df_material_item = material_data.get('material_item', pd.DataFrame())
    df_material_equal = material_data.get('material_equal', pd.DataFrame())

    if any(df.empty for df in [df_demand, df_due_lt, df_line_available, df_capa_qty,
                               df_material_qty, df_material_item]) :
        return None
    
    for i, row in df_demand.iterrows() :
        df_demand.loc[i, 'Project'] = row['Item'][3:7]
        df_demand.loc[i, "Basic2"] = row['Item'][3:8]
        df_demand.loc[i, "Tosite_group"] = row['Item'][7:8]
        df_demand.loc[i, "RMC"] = row['Item'][3:-3]
        df_demand.loc[i, "Color"] = row['Item'][8:-4]

    if 'SOP' in df_demand.columns :
        df_demand['SOP'] = df_demand['SOP'].apply(lambda x : max(0, x if pd.notna(x) else 0))
    
    processed_data = {
        'demand' : {
            'df' : df_demand,
            'items' : df_demand.to_dict('records'),
            'project_items' : {proj : group.to_dict('records')
                               for proj, group in df_demand.groupby('Project')},
            'site_items' : {site : group.to_dict('records')
                            for site, group in df_demand.groupby('Tosite_group')
                            if site and not pd.isna(site)}
        },
        'material' : process_material(df_material_qty, df_material_item, df_material_equal),
        'production' : process_production(df_line_available, df_capa_qty),
        'due_lt' : process_due_lt(df_due_lt)
    }

    return processed_data

"""
자재 관련 데이터 처리
"""
def process_material(df_material_qty, df_material_item, df_material_equal) :
    active_materials_qty = df_material_qty[df_material_qty['Active_OX'] == 'O'].copy()
    active_materials_item = df_material_item[df_material_item['Active_OX'] == 'O'].copy()

    material_availability = {}

    for _, row in active_materials_qty.iterrows() :
        material = row['Material']
        on_hand = row['On-Hand'] if pd.notna(row['On-Hand']) else 0
        available_lt = row.get('Available L/T', 0) if pd.notna(row.get('Available L/T', 0)) else 0

        material_availability[material] = {
            'on_hand' : on_hand,
            'available_lt' : available_lt
        }

    material_groups = {}

    if not df_material_equal.empty :
        for _, row in df_material_equal.iterrows() :
            group = []

            for col in ['Material A', 'Material B', 'Material C'] :
                if col in row and pd.notna(row[col]) and row[col] :
                    group.append(row[col])

            if group :
                for material in group :
                    material_groups[material] = group

    material_to_models = {}
    model_to_materials = {}

    for _, row in active_materials_item.iterrows() :
        material = row['Material']
        material_to_models[material] = []

        for i in range(1, 11) :
            col_name = f'Top_Model_{i}'

            if col_name in row and pd.notna(row[col_name]) and row[col_name] :
                pattern = row[col_name]
                material_to_models[material].append(pattern)

                if pattern not in model_to_materials :
                    model_to_materials[pattern] = []
                
                model_to_materials[pattern].append(material)

    return {
        'availability' : material_availability,
        'material_groups' : material_groups,
        'material_to_models' : material_to_models,
        'model_to_materials' : model_to_materials,
        'df_qty' : active_materials_qty,
        'df_item' : active_materials_item
    }

"""
생산 관련 데이터 처리
"""
def process_production(df_line_available, df_capa_qty) :
    project_lines = {}

    if 'Project' in df_line_available.columns :
        for _, row in df_line_available.iterrows() :
            project = str(row['Project'])
            available_lines = []

            for col in df_line_available.columns :
                if col != 'Project' and pd.notna(row[col]) and row[col] > 0 :
                    available_lines.append(col)

            project_lines[project] = available_lines

    line_capacities = {}

    if 'Line' in df_capa_qty.columns :
        df_capa_qty = df_capa_qty.set_index('Line')

    meta_prefixes = ['Max_', 'Total_', 'Sum_']
    filtered_capa_qty = df_capa_qty[~df_capa_qty.index.astype(str).str.startswith(tuple(meta_prefixes))]

    shift_columns = [col for col in filtered_capa_qty.columns if isinstance(col, int) or (isinstance(col, str) and col.isdigit())]

    for line, row in filtered_capa_qty.iterrows() :
        line_str = str(line)
        capacities = {}

        for shift in range(1, 15) :
            capacity = 0

            if shift in shift_columns :
                capacity = row[shift] if pd.notna(row[shift]) else 0

            capacities[shift] = float(capacity) if pd.notna(capacity) else 0

        line_capacities[line_str] = capacities
    
    return {
        'project_lines' : project_lines,
        'line_capacities': line_capacities,
        'df_line_available': df_line_available,
        'df_capa_qty': df_capa_qty
    }

"""
납기 정보 처리
"""
def process_due_lt(df_due_lt) :
    due_lt_map = {}

    for _, row in df_due_lt.iterrows() :
        project = row['Project']
        tosite_group = row['Tosite_group']
        due_lt = row['Due_date_LT']

        if project not in due_lt_map :
            due_lt_map[project] = {}

        due_lt_map[project][tosite_group] = due_lt

    return {
        'df' : df_due_lt,
        'due_lt_map' : due_lt_map
    }